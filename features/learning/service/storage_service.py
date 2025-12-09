import os
import json
import joblib
import tensorflow as tf
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.config import config as con
from features.learning.domain.entities.module import Module
from features.learning.domain.entities.config import Config

class StorageService:
    def __init__(self):
        self.base_dir = con.LEARNING_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _module_folder(self, module_id: str) -> Path:
        return self.base_dir / module_id

    def _module_exists(self, module_id: str) -> bool:
        return self._module_folder(module_id).exists()

    def save_module(self, module: Module, model, scaler, config: Config) -> Module:
        folder = self._module_folder(module.module_id)
        folder.mkdir(parents=True, exist_ok=True)
        # 1. Lưu model
        model_path = folder / "model.keras"
        model.save(model_path)
        module.model_path = str(model_path)
        # 2. Lưu scaler
        scaler_path = folder / "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        # 3. Lưu config.json
        config_path = folder / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)
        return module

    def load_model(self, module_id: str):
        folder = self._module_folder(module_id)
        model = tf.keras.models.load_model(folder / "model.keras")
        scaler = joblib.load(folder / "scaler.pkl")
        with open(folder / "config.json", "r") as f:
            config_data = json.load(f)
        config = Config(**config_data)
        return model, scaler, config
