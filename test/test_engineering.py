import pandas as pd
from features.engineering.input.data_input import DataInput
from features.engineering.usecase.indicator import IndicatorUseCase
from features.engineering.usecase.temporal import TemporalUseCase
from features.engineering.usecase.combine import CombineUseCase
from features.engineering.output.engineering_output import EngineeringOutput
from test_csv import to_csv

# df = IndicatorUseCase().execute("1M")
# df = TemporalUseCase().execute()
def main():
    df = EngineeringOutput().get("1M")
    # df = CombineUseCase().execute("1M")
    # df = pd.DataFrame(df)
    # print(df.head())
    to_csv(df)
    # print(df)

if __name__ == "__main__":
    main()