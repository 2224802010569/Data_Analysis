import json
import shutil
from pathlib import Path
import tensorflow as tf
from app.config import config as con
from features.learning.domain.entities.module import Module

class StorageService:

    def __init__(self):
        self.base_dir = con.LEARNING_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _module_dir(self, module_id: str) -> Path:
        return self.base_dir / module_id

    def save(self, module: Module, model) -> None:
        module_dir = self._module_dir(module.module_id)
        if module_dir.exists():
            shutil.rmtree(module_dir)
        module_dir.mkdir(parents=True, exist_ok=True)
        model_path = module_dir / "model.keras"
        model.save(model_path)
        meta_path = module_dir / "module.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(module.to_dict(), f, indent=4, ensure_ascii=False)

    def load(self, module_id: str):
        module_dir = self._module_dir(module_id)
        if not module_dir.exists():
            raise FileNotFoundError(f"Module '{module_id}' not found")
        model = tf.keras.models.load_model(module_dir / "model.keras")
        meta_path = module_dir / "module.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        module = Module(
            module_id=module_id,
            window_size=meta["window_size"],
            feature_cols=meta["feature_cols"],
            seed=meta.get("seed"),
            note=meta.get("note"),
        )
        return model, module

    def list_modules(self) -> list[str]:
        return [
            p.name
            for p in self.base_dir.iterdir()
            if p.is_dir()
        ]
