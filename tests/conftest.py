import pytest
import os
from pytest_httpserver import HTTPServer
import pandas as pd
from source.entities.job_info import JobInfo


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def setup_mock_server(http_server: HTTPServer):
    ####
    # Set up mock server using html files in `vercel_clone`; I've copied the files locally so
    # we can test on local http-server. If the html ever changes on Vercel's website, consider
    # retaining the current function so that we have an example that is tested from local files.
    # The main advantage is that we can test changes more quickly (e.g. adding additional fields
    # to JobInfo object) compared with hitting external server each time.)
    ####
    def get_html(path: str) -> str:
        with open(path, 'r') as handle:
            return handle.read()
    # setup mock server for /careers page
    careers_html = get_html('tests/test_files/vercel_clone/vercel_careers_clone.html')
    http_server.expect_request("/careers").respond_with_data(careers_html)
    # setup mock server for each of the job's pages
    jobs_path = 'tests/test_files/vercel_clone/careers'
    html_files = os.listdir(jobs_path)
    for file in html_files:
        job_html = get_html(os.path.join(jobs_path, file))
        mock_path = os.path.join("/careers", file.removesuffix('.html'))
        http_server.expect_request(mock_path).respond_with_data(job_html)


@pytest.fixture(scope='function')
def mock_job_info_list() -> list[JobInfo]:
    return [
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


@pytest.fixture(scope='function')
def mock_job_object_dataframe() -> pd.DataFrame:
    return pd.DataFrame(dict(
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
