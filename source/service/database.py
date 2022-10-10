from datetime import datetime
from helpsk.database import Database
from helpsk.pandas import relocate
from source.entities.job_info import JobInfo, from_dataframe, to_dataframe


def datetime_now_utc() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def save_job_infos(database: Database, jobs: list[JobInfo], snapshot: datetime):
    df = to_dataframe(jobs=jobs)
    df['snapshot'] = snapshot  # datetime.now().strftime('%Y-%m-%d %h:%M:%s')
    df = relocate(df, column='snapshot', before='company')
    with database:
        database.insert_records(dataframe=df, table='JOBS')


def load_job_infos(database: Database, latest_snapshots: bool = True) -> list[JobInfo]:
    """
    This function queries the database and returns a list of JobInfos.

    Args:
        database:
            the database object
        latest_snapshots:
            If `True`, return the JobInfos corresponding to records with the latest snapshot
            timestamp.
            If `False`, return a list of JobInfo objects corresponding to all records; Note that if
            there are multiple snapshots for the same company/title, this will result in a
            non-sensical list with duplicated jobs.
    """
    if latest_snapshots:
        query = 'SELECT * FROM JOBS WHERE snapshot = (SELECT MAX(snapshot) FROM JOBS)'
    else:
        query = 'SELECT * FROM JOBS'
    with database:
        df = database.query(sql=query)
    return from_dataframe(df=df)
