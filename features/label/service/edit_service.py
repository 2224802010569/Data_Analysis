import pandas as pd
from features.label.domain.entities.label import Label

class EditService:
    def convert(self, df: pd.DataFrame) -> list[Label]:
        df = df.copy()
        df["timestamp_next"] = df["timestamp"].shift(-1)
        df["timestamp_next"] = df["timestamp_next"].fillna(df["timestamp"])
        labels: list[Label] = []
        timeframe = df["timeframe"].iloc[0]
        for _, row in df.iterrows():
            labels.append(
                Label(
                    label=row["label"],
                    timeframe=timeframe,
                    t0=row["timestamp"],
                    t1=row["timestamp_next"]
                )
            )
        return labels

    def merge(self, labels: list[Label]) -> list[Label]:
        if not labels:
            return []
        labels = sorted(labels, key=lambda x: x.t0)
        merged = []
        cur = labels[0]
        for nxt in labels[1:]:
            if nxt.label == cur.label and nxt.t0 == cur.t1:
                cur = Label(
                    label=cur.label,
                    timeframe=cur.timeframe,
                    t0=cur.t0,
                    t1=nxt.t1
                )
            else:
                merged.append(cur)
                cur = nxt
        merged.append(cur)
        return merged