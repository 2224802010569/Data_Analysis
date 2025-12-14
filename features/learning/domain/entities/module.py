from dataclasses import dataclass
from typing import Optional

@dataclass
class Module:
    module_id: str          
    window_size: int
    feature_cols: list[str]
    seed: Optional[int] = None
    note: Optional[str] = None
    def to_dict(self):
        return {
            "window_size": self.window_size,
            "feature_cols": self.feature_cols,
            "seed": self.seed,
        }        
