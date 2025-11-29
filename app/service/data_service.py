from features.data.output.data_output import DataOutput

class DataService:
    def __init__(self):
        self.data_output = DataOutput()

    def get_candle_data(self, timeframe: str):
        try:
            df = self.data_output.get(timeframe=timeframe)
            df = df.sort_values("timestamp")
            return df
        except Exception as e:
            print("[DataService] Error:", e)
            return None
