from features.data.output.data_output import DataOutput
class DataService:
    def get_candle_data(self, timeframe: str):
        try:
            df = DataOutput().get(timeframe=timeframe)
            df = df.sort_values("timestamp")
            return df
        except Exception as e:
            print("[DataService] Error:", e)
            return None

    