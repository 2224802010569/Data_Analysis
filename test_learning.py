import pandas as pd
from features.learning.output.learning_output import LearningOutput
from features.learning.usecase.load import LoadUseCase
from features.learning.usecase.fetch_and_save import FetchAndSaveUseCase
from features.learning.usecase.train import TrainUseCase
from features.learning.domain.entities.config import Config
from test_csv import to_csv

def main():
    uc = LearningOutput().get()
    print(uc)

if __name__ == "__main__":
    main()
