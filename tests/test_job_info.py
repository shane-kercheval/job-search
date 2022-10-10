import pandas as pd
from helpsk.validation import dataframes_match

from source.entities.job_info import JobInfo, from_dataframe, to_dataframe


def test_to_from_dataframe():
    expected_jobs = [
        JobInfo(
            company='A',
            title='Data Scientist',
            location='Remote',
            url='test.com/ds',
            description="You'll do this and that.",
        ),
        JobInfo(
            company='B',
            title='Senior Data Scientist',
            location='US/Remote',
            url='test.com/sds',
            description="You'll do this and that x2.",
        ),
        JobInfo(
            company='C',
            title='Staff Data Scientist',
            location='West Coast / Remote',
            url='test.com/staffds',
            description="You'll do this and that x10.",
        ),
    ]
    expected_df = pd.DataFrame(dict(
        company=['A', 'B', 'C'],
        title=['Data Scientist', 'Senior Data Scientist', 'Staff Data Scientist'],
        location=['Remote', 'US/Remote', 'West Coast / Remote'],
        url=['test.com/ds', 'test.com/sds', 'test.com/staffds'],
        description=[
            "You'll do this and that.",
            "You'll do this and that x2.",
            "You'll do this and that x10."
        ],
    ))

    actual_df = to_dataframe(jobs=expected_jobs)
    assert dataframes_match(dataframes=[expected_df, actual_df])

    actual_jobs = from_dataframe(df=actual_df)
    assert all(a == e for a, e in zip(actual_jobs, expected_jobs))
