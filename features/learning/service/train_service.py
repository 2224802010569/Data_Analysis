from features.learning.service.data_service import DataService
from features.learning.service.model_service import ModelService


class TrainService:

    def __init__(self):
        self.data_service = DataService()
        self.model_service = ModelService()

    def train(self,module,timeframe: str, epochs: int,batch_size: int,):
        df_candle, df_engineering = self.data_service.load_data(
            timeframe=timeframe
        )
        X, y = self.data_service.build_training_set(
            df_candle=df_candle,
            df_engineering=df_engineering,
            module=module,
        )
        if len(X) == 0:
            raise ValueError(f"No training data for timeframe {timeframe}")
        window_size, num_features = X.shape[1:]
        model = self.model_service.build_model(
            window_size=window_size,
            num_features=num_features,
        )
        self.model_service.train(model,X,y)
        return model, df_candle, df_engineering
