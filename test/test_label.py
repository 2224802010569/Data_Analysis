import pandas as pd
from features.label.usecase.fetch_and_save import FetchAndSaveUseCase
from features.label.usecase.load import LoadUseCase
from features.label.usecase.labels import LabelUsecase
from test_csv import to_csv

def main():
    FetchAndSaveUseCase().execute()
    df = LoadUseCase().load()
    df = pd.DataFrame([vars(label) for label in df])
    to_csv(df)

if __name__ == "__main__":
    main()