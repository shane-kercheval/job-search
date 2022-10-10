from datetime import datetime
import pandas as pd
from source.entities.job_info import JobInfo, from_dataframe, to_dataframe
from helpsk.database_base import Database
from helpsk.pandas import relocate


def save_job_infos(database: Database, jobs: list[JobInfo], snapshot: datetime):
    df = to_dataframe(jobs=jobs)
    df['snapshot'] = snapshot  # datetime.now().strftime('%Y-%m-%d %h:%M:%s')
    df = relocate(df, column='snapshot', before='company')
    with database:
        database.insert_records(dataframe=df, table='JOBS')


def load_job_infos(database: Database) -> pd.DataFrame:
    with database:
        df = database.query('SELECT * FROM JOBS')
    return from_dataframe(df=df)


def load_job_infos_latest(database: Database) -> pd.DataFrame:
    with database:
        df = database.query('SELECT * FROM JOBS WHERE snapshot = (SELECT MAX(snapshot) FROM JOBS)')
    return from_dataframe(df=df)
