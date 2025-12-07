import math
from features.label.output.label_output import LabelOutput

class LabelService:
    def get_label_data(self, timeframe: str):
        try:
            df = LabelOutput().get(timeframe=timeframe)
            return df
        except Exception as e:
            print("[LabelService] Error:", e)
            return None
    
    def get_page(self, tf: str, page: int, page_size: int = 20):
        df = self.get_label_data(tf)
        df = self._filter_labels(df)
        df = df.sort_values("t0")
        if df is None:
            return self._empty_page(page)
        total_pages = self._calc_total_pages(len(df), page_size)
        page = self._fix_page_bounds(page, total_pages)
        records = self._slice_page(df, page, page_size)
        normalized = self._normalize_records(records)
        return {
            "page": page,
            "total_pages": total_pages,
            "records": normalized
        }

    def _empty_page(self, page):
        return {
            "page": page,
            "total_pages": 1,
            "records": []
        }

    def _calc_total_pages(self, total_records, page_size):
        return max(1, math.ceil(total_records / page_size))

    def _fix_page_bounds(self, page, total_pages):
        if page < 1:
            return 1
        if page > total_pages:
            return total_pages
        return page

    def _slice_page(self, df, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        return df.iloc[start:end].to_dict(orient="records")

    def _normalize_records(self, records):
        normalized = []
        for r in records:
            normalized.append({
                "t0": r.get("t0") or r.get("timestamp_start") or None,
                "t1": r.get("t1") or r.get("timestamp_end") or None,
                "label": r.get("label") or r.get("Label") or r.get("action") or "none",
            })
        return normalized
    
    def _filter_labels(self, df):
        hidden_labels=["none", "normal"]
        if not hidden_labels:
            return df
        hidden = set([x.lower() for x in hidden_labels])
        df = df[~df["label"].astype(str).str.lower().isin(hidden)]

        return df
