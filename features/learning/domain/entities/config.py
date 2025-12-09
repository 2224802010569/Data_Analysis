from dataclasses import dataclass

@dataclass
class Config:
    seed: int
    window_size: int
    num_classes: int
    feature_cols: list[str]
    note: str = ""