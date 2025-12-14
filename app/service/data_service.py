# from features.data.output.data_output import DataOutput
from features.learning.output.learning_output import LearningOutput
class DataService:
    def get_candle_data(self, timeframe: str):
        try:
            # df = DataOutput().get(timeframe=timeframe)
            df = LearningOutput().get(timeframe)
            df = df.sort_values("timestamp")
            return df
        except Exception as e:
            print("[DataService] Error:", e)
            return None

    