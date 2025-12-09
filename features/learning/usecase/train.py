import json
import os
import uuid
import random
from typing import Optional
from features.learning.input.data_input import DataInput
from features.learning.input.engineering_input import EngineeringInput
from features.learning.input.label_input import LabelInput
from features.learning.service.data_train_service import DataTrainService
from features.learning.service.scaling_service import ScalingService
from features.learning.service.model_service import ModelService
from features.learning.service.metric_service import MetricService
from features.learning.service.history_service import HistoryService
from features.learning.service.storage_service import StorageService
from features.learning.domain.entities.config import Config
from features.learning.domain.entities.module import Module

class TrainUseCase:

    def __init__(self):
        self.data_input = DataInput()
        self.eng_input = EngineeringInput()
        self.label_input = LabelInput()
        self.data_service = DataTrainService()
        self.scaler_service = ScalingService()
        self.model_service = ModelService()
        self.metric_service = MetricService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    def _resolve_module_id(self, module_id: Optional[str]) -> str:
        return module_id or uuid.uuid4().hex[:5]

    def _load_raw_data(self, timeframe: str):
        df_data = self.data_input.load(timeframe=timeframe)
        df_eng = self.eng_input.load(timeframe=timeframe)
        df_label = self.label_input.load(timeframe=timeframe)
        return df_data, df_eng, df_label

    def _prepare_config(self, df_eng, user_config: Optional[Config]) -> Config:
        if user_config is not None:
            cfg = user_config
        else:
            cfg = Config(
                seed=None,
                window_size=35,
                num_classes=6,
                feature_cols=list(df_eng.columns),
                note="auto-generated config",
            )
        if cfg.seed is None:
            cfg.seed = random.randint(1, 99999)
        return cfg

    def _apply_meta_learning(self, cfg: Config, timeframe: str):
        global_history = self.history_service.load_global_history()
        meta_pool = global_history.get("meta_pool", [])
        if not meta_pool:
            return cfg
        best = max(meta_pool, key=lambda x: x["accuracy"])
        best_cfg = best["config"]
        ws = best_cfg["window_size"] + random.randint(-10, 10)
        cfg.window_size = max(10, min(ws, 80))
        features = list(best_cfg["feature_cols"])
        if random.random() < 0.2 and len(features) > 5:
            features.pop()
        all_cols = list(self.eng_input.load(timeframe=timeframe).columns)
        if random.random() < 0.2:
            new_f = random.choice(all_cols)
            if new_f not in features:
                features.append(new_f)
        cfg.feature_cols = features
        cfg.seed = random.randint(1, 100)
        return cfg


    def _train_model(self, df_data, df_eng, df_label, cfg, module_id, timeframe):
        X, y = self.data_service.build_training_set(df_data, df_eng, df_label, cfg)
        if X.size == 0:
            raise ValueError("Không đủ dữ liệu để tạo window training.")
        scaler, X_scaled = self.scaler_service.scale_features(X)
        model = self.model_service.build_model(
            window_size=cfg.window_size,
            num_features=X.shape[-1],
            num_classes=cfg.num_classes,
        )
        history_obj = self.model_service.train(model, X_scaled, y)
        metrics = self.metric_service.create_metrics(history_obj, module_id)
        metrics["timeframe"] = timeframe
        history = self.metric_service.create_history(history_obj, cfg, module_id)
        return model, scaler, metrics, history

    def _build_module_entity(self, module_id, cfg: Config) -> Module:
        return Module(
            module_id=module_id,
            seed=cfg.seed,
            feature_cols=cfg.feature_cols,
            note=cfg.note,
        )
    
    def execute(self,timeframe: str,module_id: Optional[str] = None,config: Optional[Config] = None):
        module_id = self._resolve_module_id(module_id)
        df_data, df_eng, df_label = self._load_raw_data(timeframe)
        cfg = self._prepare_config(df_eng, config)
        cfg = self._apply_meta_learning(cfg, timeframe)
        model, scaler, metrics, history = self._train_model(
            df_data=df_data,
            df_eng=df_eng,
            df_label=df_label,
            cfg=cfg,
            module_id=module_id,
            timeframe=timeframe,
        )
        module_entity = self._build_module_entity(module_id, cfg)
        module_entity = self.storage_service.save_module(
            module=module_entity,
            model=model,
            scaler=scaler,
            config=cfg
        )
        self.history_service.save_history(module_entity.module_id, history)
        module_entity = self.storage_service.save_module(
            module=module_entity,
            model=model,
            scaler=scaler,
            config=cfg
        )
        self.history_service.save_history(module_entity.module_id, history)
        metrics_path = os.path.join(
            self.history_service.base_path,
            module_entity.module_id,
            "metrics.json"
        )
        self.metric_service.append_total_metrics(
            module_id=module_entity.module_id,
            accuracy=metrics["accuracy"],
            timeframe=timeframe
        )
        self.history_service.append_history_item(
            module_id=module_entity.module_id,
            accuracy=metrics["accuracy"],
            config=cfg.__dict__
        )
        self.history_service.update_best()
        self.history_service.update_meta_pool()
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4, ensure_ascii=False)
        return module_entity