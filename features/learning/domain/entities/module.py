from dataclasses import dataclass

@dataclass
class Module:
    module_id: str          
    seed: int               
    feature_cols: list[str] 
    note: str = ""          
