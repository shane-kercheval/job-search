import os
import pandas as pd
from helpsk.database import Sqlite
from source.entities.job_info import JobInfo, from_dataframe
from source.service.database import save_job_infos, load_job_infos, \
    datetime_now_utc


def test_to_from_database(
        mock_job_info_list: list[JobInfo],
        mock_job_object_dataframe: pd.DataFrame):

    db_path = 'tests/test.db'
    try:
        db = Sqlite(path=db_path)
        assert not os.path.exists(db_path)

        # Save jobs to database
        snapshot = datetime_now_utc()
        save_job_infos(
            database=db,
            jobs=mock_job_info_list,
            snapshot=snapshot
        )
        assert os.path.exists(db_path)

        # Load jobs from database
        found_jobs = load_job_infos(db)
        assert all(a == e for a, e in zip(found_jobs, mock_job_info_list))

        # Load latest jobs from database (should be the same in this case)
        found_jobs = load_job_infos(db, latest_snapshots=False)
        assert all(a == e for a, e in zip(found_jobs, mock_job_info_list))

        # Load all records from database, which contains snapshot column.
        with db:
            found_records = db.query('SELECT * FROM JOBS')

        assert (found_records['snapshot'] == snapshot).all()
        found_jobs = from_dataframe(df=found_records)
        assert all(a == e for a, e in zip(found_jobs, mock_job_info_list))

    finally:
        os.remove(db_path)
