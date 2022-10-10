from source.entities.job_info import JobInfo, from_dataframe, to_dataframe
from helpsk.database_base import Database
from helpsk.pandas import relocate


def save_job_infos(database: Database, jobs: list[JobInfo]):
    df = to_dataframe(jobs=jobs)
    from datetime import datetime

    df['snapshot'] = datetime.now().strftime('%Y-%m-%d %h:%M:%s')
    df = relocate(df, column='snapshot', before='title')

    with database:
        database.insert_records(dataframe=df, table='JOBS')


def load_job_infos(database: Database):
    with database:
        df = database.query('SELECT * FROM JOBS')

    return from_dataframe(df=df)
