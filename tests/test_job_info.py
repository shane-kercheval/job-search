import pandas as pd
from helpsk.validation import dataframes_match

from source.entities.job_info import JobInfo, from_dataframe, to_dataframe


def test_to_from_dataframe(
        mock_job_info_list: list[JobInfo],
        mock_job_object_dataframe: pd.DataFrame):

    actual_df = to_dataframe(jobs=mock_job_info_list)
    assert dataframes_match(dataframes=[mock_job_object_dataframe, actual_df])

    actual_jobs = from_dataframe(df=actual_df)
    assert all(a == e for a, e in zip(actual_jobs, mock_job_info_list))
