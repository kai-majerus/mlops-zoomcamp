from prefect import flow, task

@task
def load_data():
    return 1

@task
def transform_data(x):
    return x * 2

@task
def save_data(result):
    print(f"Final result: {result}")

@flow
def my_pipeline():
    data = load_data()
    transformed = transform_data(data)
    save_data(transformed)

if __name__ == "__main__":
    my_pipeline()
