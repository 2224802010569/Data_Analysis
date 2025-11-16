import pandas as pd
from features.label.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.label.usecase.load import LoadUseCase
from test_csv import to_csv

def main():
    FetchAndSaveDataUseCase().execute()
    df = LoadUseCase().load("1M")
    df = pd.DataFrame(df)
    to_csv(df)

if __name__ == "__main__":
    main()