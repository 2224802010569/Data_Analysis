import pandas as pd
from features.data.output.data_output import DataOutput
from features.engineering.input.learning_input import LearningInput
from features.learning.input.data_input import DataInput
from features.engineering.output.engineering_output import EngineeringOutput
from features.label.output.label_output import LabelOutput

from test_csv import to_csv

def main():
    # df = DataInput().load()
    # to_csv("data",df)

    df = LabelOutput().get("1d")
    to_csv("label",df)

    # df = EngineeringOutput().get()
    # to_csv("eng",df)

    # df = LearningOutput().get("1d")
    # to_csv("learn",df)

    # df = LearningInput().load()
    # to_csv("learn",df)

if __name__ == "__main__":
    main()