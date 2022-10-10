import os
from time import sleep
import pandas as pd
from helpsk.database import Sqlite
from helpsk.pandas import relocate
from helpsk.validation import dataframes_match

from tests.conftest import create_fake_job_info_list

from source.entities.job_info import JobInfo, from_dataframe, to_dataframe
from source.service.database import save_job_infos, load_job_infos, \
    datetime_now_utc


def test_save_load_job_infos(
        fake_job_info_list: list[JobInfo],
        fake_job_object_dataframe: pd.DataFrame):

    db_path = 'tests/test.db'
    try:
        db = Sqlite(path=db_path)
        assert not os.path.exists(db_path)

        # Save jobs to database
        first_snapshot = datetime_now_utc()
        save_job_infos(
            database=db,
            jobs=fake_job_info_list,
            snapshot=first_snapshot
        )
        assert os.path.exists(db_path)

        # Load jobs from database
        found_jobs = load_job_infos(db)
        assert all(a == e for a, e in zip(found_jobs, fake_job_info_list))

        # Load latest jobs from database (should be the same in this case)
        found_jobs = load_job_infos(db, latest_snapshots=False)
        assert all(a == e for a, e in zip(found_jobs, fake_job_info_list))

        # Load all records from database, which contains snapshot column.
        with db:
            found_records = db.query('SELECT * FROM JOBS')

        assert (found_records['snapshot'] == first_snapshot).all()
        assert dataframes_match(dataframes=[
            found_records.drop(columns='snapshot'),
            fake_job_object_dataframe
        ])
        found_jobs = from_dataframe(df=found_records)
        assert all(a == e for a, e in zip(found_jobs, fake_job_info_list))

        # insert new set of JobInfo objects
        second_fake_list = create_fake_job_info_list(length=5)
        sleep(1)
        second_snapshot = datetime_now_utc()
        assert first_snapshot != second_snapshot
        save_job_infos(
            database=db,
            jobs=second_fake_list,
            snapshot=second_snapshot
        )
        # check that the newly inserted jobs are retrieved correctly
        found_job_infos = load_job_infos(db)
        assert len(found_job_infos) == len(second_fake_list)
        assert all(a == e for a, e in zip(found_job_infos, second_fake_list))

        # now check all records
        with db:
            found_records = db.query('SELECT * FROM JOBS')

        assert len(found_records) == len(fake_job_info_list) + len(second_fake_list)
        # create expected dataframe
        expected_df = pd.concat([fake_job_object_dataframe, to_dataframe(second_fake_list)]).\
            reset_index(drop=True)
        expected_df['snapshot'] = [first_snapshot] * len(fake_job_object_dataframe) + \
            [second_snapshot] * len(second_fake_list)
        expected_df = relocate(df=expected_df, column='snapshot', before='company')

        assert set(found_records['snapshot'].unique()) == set([first_snapshot, second_snapshot])
        assert dataframes_match(dataframes=[found_records, expected_df])
        found_jobs = from_dataframe(df=found_records)
        assert all(a == e for a, e in zip(found_jobs[:3], fake_job_info_list))
        assert all(a == e for a, e in zip(found_jobs[3:], second_fake_list))

    finally:
        os.remove(db_path)
