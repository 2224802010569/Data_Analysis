import pandas as pd
from features.engineering.output.engineering_output import EngineeringOutput
from features.label.output.label_output import LabelOutput

from test_csv import to_csv

def main():
    df = LabelOutput().get()
    # df = EngineeringOutput().get()
    to_csv(df)

if __name__ == "__main__":
    main()