import os
import pandas as pd
from helpsk.database import Sqlite
from helpsk.pandas import relocate
from helpsk.validation import dataframes_match

from source.entities.job_info import JobInfo, from_dataframe
from source.service.database import save_job_infos, load_job_infos, \
    datetime_now_utc


def test_save_load_job_infos(
        mock_job_info_list: list[JobInfo],
        mock_job_object_dataframe: pd.DataFrame):

    db_path = 'tests/test.db'
    try:
        db = Sqlite(path=db_path)
        assert not os.path.exists(db_path)

        # Save jobs to database
        first_snapshot = datetime_now_utc()
        save_job_infos(
            database=db,
            jobs=mock_job_info_list,
            snapshot=first_snapshot
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

        assert (found_records['snapshot'] == first_snapshot).all()
        assert dataframes_match(dataframes=[
            found_records.drop(columns='snapshot'),
            mock_job_object_dataframe
        ])
        found_jobs = from_dataframe(df=found_records)
        assert all(a == e for a, e in zip(found_jobs, mock_job_info_list))

        second_snapshot = datetime_now_utc()
        save_job_infos(
            database=db,
            jobs=mock_job_info_list,
            snapshot=second_snapshot
        )

        with db:
            found_records = db.query('SELECT * FROM JOBS')

        expected_df = pd.concat([mock_job_object_dataframe, mock_job_object_dataframe]).\
            reset_index(drop=True)
        expected_df['snapshot'] = [
            first_snapshot, first_snapshot, first_snapshot,
            second_snapshot, second_snapshot, second_snapshot,
        ]
        expected_df = relocate(df=expected_df, column='snapshot', before='company')

        assert len(found_records) == 6
        assert set(found_records['snapshot'].unique()) == set([first_snapshot, second_snapshot])
        assert dataframes_match(dataframes=[found_records, expected_df])
        found_jobs = from_dataframe(df=found_records)
        assert all(a == e for a, e in zip(found_jobs[:3], mock_job_info_list))
        assert all(a == e for a, e in zip(found_jobs[3:], mock_job_info_list))
        # new_job_list = [j.copy() for j in mock_job_info_list]
        # new_job_list[0].company = '1'
        # mock_job_info_list[0]

    finally:
        os.remove(db_path)
