from typing import Protocol
from features.engineering.domain.entities.feature_set import FeatureSet

class FeatureRepositoryPort(Protocol):
    def save(self, feature_set: FeatureSet) -> None:
        pass

    def load(self, timeframe: str) -> FeatureSet:
        pass
