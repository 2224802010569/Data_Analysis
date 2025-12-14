from features.learning.usecase.forecast import ForecastUseCase
from features.learning.usecase.train import TrainUseCase
from test_csv import to_csv
from app.config import config as con

def test_train():
    uc = TrainUseCase()
    print("🚀 Start training test...")
    result = uc.execute()
    print("✅ Train finished")
    print("Module ID:", result["module_id"])
    for tf, metrics in result["metrics"].items():
        print(f"Timeframe: {tf}")
        for k, v in metrics.items():
            print(f"  {k}: {v}")

def test_forecast():
    uc = ForecastUseCase()
    # for tf in con.TIMEFRAMES:
    #     d = uc.execute(
    #         module_id="00000",
    #         timeframe=tf,
    #     )
    d = uc.execute(
        module_id="00000",
        timeframe="1d",
    )
    print(d)

def test_load():
    from features.learning.usecase.load import LoadUseCase
    uc = LoadUseCase()
    print("🚀 Start load test...")
    df = uc.load(timeframe="1M")
    print("✅ Load finished")
    print(df.head())

def test_workflow():
    from features.learning.workflow.learning_workflow import LearningWorkflow
    workflow = LearningWorkflow()
    print("🚀 Start workflow test...")
    df = workflow.run(timeframe="1M")
    print("✅ Workflow finished")
    print(df.head())

def test_out():
    from features.learning.output.learning_output import LearningOutput
    output = LearningOutput()
    print("🚀 Start output test...")
    df = output.get()
    print("✅ Output finished")
    to_csv("fore", df)

if __name__ == "__main__":
    # test_train()
    # test_forecast()
    # test_workflow()
    # test_load()
    test_out()
