import pandas as pd
from features.learning.usecase.train import TrainUseCase
from features.learning.domain.entities.config import Config
from test_csv import to_csv


def test_print(title):
    print("\n" + "=" * 60)
    print("==  " + title)
    print("=" * 60)


def run_single_train(timeframe: str, user_config: Config = None):
    uc = TrainUseCase()

    model, scaler, metrics, history, module_entity = uc.execute(
        timeframe=timeframe,
        module_id=None,          
        config=user_config,
    )

    print(f"module_id       : {module_entity.module_id}")
    print(f"seed            : {module_entity.seed}")
    print(f"feature_cols    : {len(module_entity.feature_cols)} cols")
    print(f"accuracy        : {metrics['accuracy']:.4f}")
    print(f"loss            : {metrics['loss']:.4f}")
    print(f"history-epochs  : {history['epochs']}")
    print(f"window_size     : {history['window_size']}")
    return metrics, history, module_entity


def main():
    metrics, history, module_entity = run_single_train("1d")
    print("Metrics",type(metrics))
    print("History",type(history))
    print("Module Entity",type(module_entity))

if __name__ == "__main__":
    main()
