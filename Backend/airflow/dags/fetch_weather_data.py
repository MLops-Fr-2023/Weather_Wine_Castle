import requests
from datetime import timedelta, datetime
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import os

user_name = os.environ.get('API_USER')
pwd = os.environ.get('API_PWD')

cities = {
    "Arsac": "Arsac", 
    "Ludon-Medoc": "Ludon-Medoc", 
    "Castelnau-de-Medoc": "Castelnau-de-Medoc",
    "Soussan": "Soussan", 
    "Margaux": "Margaux",
    "Lamarque": "Lamarque, FR",
    "Macau": "Macau, FR"
    }

my_dag = DAG(
    dag_id='fetch_weather_dag',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval=timedelta(hours=3),
    default_args={
        'start_date': datetime.now()},
    catchup=True)

def get_token():
    print('get token')
    url_token = 'http://api:8000/token'
    headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"}
    data = {
    "grant_type": "",
    "username": user_name,
    "password": pwd,
    "scope": "",
    "client_id": "",
    "client_secret": ""}
    answer = requests.post(url_token, headers=headers, data=data)
    token_type = answer.json()['token_type']
    access_token = answer.json()['access_token']
    Variable.set(key = 'token_type', value = token_type)
    Variable.set(key = 'access_token', value = access_token)

def fetch_weather_data():
    print('fetch_weather_data running')
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = 'http://api:8000/update_weather_data'
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return 'fetch_weather_data terminated'

def delete_forecast_data():
    print('delete forecast data')
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = 'http://api:8000/delete_forecast_data/'
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return 'Forecast data deleted'

def forecast_data(city):
    print('forecast data '+str(city))
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = 'http://api:8000/forecast_city/{city}?name_city='+str(city)
    print(url)
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return f'process_raw_data terminated for {city}'


get_token = PythonOperator(
    task_id='get_token',
    python_callable=get_token,
    dag=my_dag,
    doc="""use api root token to have it""")

fetch_weather_data = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=my_dag,
    doc="""use api root token to have it
            use api root to  update data""")

delete_forecast_data = PythonOperator(
    task_id='delete_forecast_data',
    python_callable=delete_forecast_data,
    dag=my_dag,
    doc="""use api root to delete forecast data""")

# Define the tasks to call the function with different arguments
for city_key, city_value in cities.items():
    task = PythonOperator(
        task_id=f"Forecast_for_{city_key}",
        python_callable=forecast_data,
        op_args=[city_value],  # Pass the city value as a list
        dag=my_dag)
        
    get_token >> [fetch_weather_data, delete_forecast_data] >> task

