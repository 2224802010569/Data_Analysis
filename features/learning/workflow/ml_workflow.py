import sys
import os
current = os.path.abspath(os.path.dirname(__file__))
while current != "/" and current != "":
    if "features" in os.listdir(current):
        sys.path.insert(0, current)
        break
    current = os.path.abspath(os.path.join(current, ".."))
from features.learning.usecase.fetch_and_save import FetchAndSaveUseCase


def run():
    FetchAndSaveUseCase().execute("1d")
    print("Complete")

if __name__ == "__main__":
    run()
