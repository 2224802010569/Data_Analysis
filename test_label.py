import pandas as pd
from features.label.usecase.fetch_and_save import FetchAndSaveUseCase
from features.label.usecase.load import LoadUseCase
from features.label.usecase.labels import LabelUsecase
from features.label.workflow.label_workflow import LabelWorkflow
from features.label.output.label_output import LabelOutput

from test_csv import to_csv

def main():
    # FetchAndSaveUseCase().execute()
    # df = LoadUseCase().load()
    # df=LabelWorkflow().run()
    df = LabelOutput().get()
    # df = pd.DataFrame([vars(label) for label in df])
    to_csv(df)

if __name__ == "__main__":
    main()