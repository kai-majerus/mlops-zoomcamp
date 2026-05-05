from duration_prediction import read_dataframe, create_X, train_model

from prefect import flow, task

from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_dates():
    today = datetime.today()

    train_date = today - relativedelta(months=5)
    val_date = today - relativedelta(months=4)

    return (
        train_date.year,
        train_date.month,
        val_date.year,
        val_date.month
    )

# ======================
# PREFECT TASKS (WRAPPERS)
# ======================


@task
def load_data(year, month):
    return read_dataframe(year, month)


@task
def prepare_features(df, dv=None):
    return create_X(df, dv)


@task
def train(X_train, y_train, X_val, y_val, dv):
    return train_model(X_train, y_train, X_val, y_val, dv)


# ======================
# PREFECT FLOW (PIPELINE)
# ======================

@flow
def taxi_training_pipeline(year: int | None = None, month: int | None = None):

    if year is None or month is None:
        # default behavior (current schedule)
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        today = datetime.today()
        train_date = today - relativedelta(months=5)
        val_date = today - relativedelta(months=4)

        train_year, train_month = train_date.year, train_date.month
        val_year, val_month = val_date.year, val_date.month
    else:
        # backfill mode
        train_year, train_month = year, month

        # validation = next month
        if month == 12:
            val_year, val_month = year + 1, 1
        else:
            val_year, val_month = year, month + 1

    print(f"Train: {train_year}-{train_month}")
    print(f"Val: {val_year}-{val_month}")
    df_train = load_data(train_year, train_month)
    df_val = load_data(val_year, val_month)

    X_train, dv = prepare_features(df_train)
    X_val, _ = prepare_features(df_val, dv)

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    run_id = train(X_train, y_train, X_val, y_val, dv)

    print(f"MLflow run_id: {run_id}")

    with open("run_id.txt", "w") as f:
        f.write(run_id)

    return run_id

# ======================
# ENTRY POINT
# ======================


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, required=False)
    parser.add_argument('--month', type=int, required=False)
    parser.add_argument('--serve', action='store_true', help="Run Prefect scheduler")

    args = parser.parse_args()

    if args.serve:
        # START SCHEDULER (does NOT run pipeline immediately)
        taxi_training_pipeline.serve(
            name="my-first-deployment",
            cron="5 9 * * *"
        )
    else:
        # RUN PIPELINE IMMEDIATELY (manual / backfill mode)
        taxi_training_pipeline(year=args.year, month=args.month)
