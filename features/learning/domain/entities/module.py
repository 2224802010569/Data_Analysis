from dataclasses import dataclass

@dataclass
class Module:
    module_id: str          # UUID
    seed: int               # seed dùng khi train
    feature_cols: list[str] # các feature đã dùng để train
    note: str = ""          # ghi chú
