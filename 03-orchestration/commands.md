- cd into mlflow_data
- start the server in one terminal

mlflow server \
    --backend-store-uri sqlite:///mlflow.db

- run the script in another terminal

python ../duration-prediction.py --year=2021 --month=1
