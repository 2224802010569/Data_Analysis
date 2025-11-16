import asyncio

import pandas as pd
from features.data.output.data_output import DataOutput
from features.data.usecase.fetch_and_save_data import FetchAndSaveDataUseCase
from features.data.usecase.load import LoadUseCase


def main():
    #Lấy dữ liệu gốc từ ccxt và lưu CSV
    # print("\n--- [1] FETCH & SAVE DATA ---")
    # fetch_uc = FetchAndSaveDataUseCase()
    # await fetch_uc.execute()

    # #Làm sạch dữ liệu
    # print("\n--- [2] CLEAN DATA ---")
    # clean_uc = CleanDataUseCase()
    # clean_uc.execute(fill_missing=True)

    # #Hợp nhất dữ liệu đã làm sạch thành 1 file tổng hợp
    # print("\n--- [3] MERGE DATA ---")
    # merge_uc = MergeDataUseCase()
    # merged_df = merge_uc.execute()
    # if merged_df is not None:
    #     print(f"\n✅ Final merged data: {len(merged_df)} rows, {len(merged_df.columns)} columns")

    # Lấy dữ liệu để dùng
    # print("\n--- [4] LOAD DATA ---")
    # loader = LoadUseCase()
    # # df = pd.DataFrame(loader.load(type="csv"))
    # df = pd.DataFrame(loader.load(timeframe="1h"))
    # print(df.head(2))

    df = DataOutput().get()
    print(df)

if __name__ == "__main__":
    main()