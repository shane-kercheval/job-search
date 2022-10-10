from typing import Optional
import pytest
import os
from pytest_httpserver import HTTPServer
import pandas as pd
from faker import Faker
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


def create_fake_job_info(seed: Optional[int] = None) -> JobInfo:
    fake = Faker()
    if seed:
        Faker.seed(seed=seed)
    return JobInfo(
            company=fake.company(),
            title=fake.job(),
            location=fake.state(),
            url=fake.url(),
            description=fake.pystr(),
        )


def create_fake_job_info_list(length: int) -> list[JobInfo]:
    return [create_fake_job_info() for _ in range(length)]


@pytest.fixture(scope='function')
def mock_job_info_list() -> list[JobInfo]:
    return create_fake_job_info_list(3)


@pytest.fixture(scope='function')
def mock_job_object_dataframe(mock_job_info_list) -> pd.DataFrame:
    return pd.DataFrame(dict(
        company=[j.company for j in mock_job_info_list],
        title=[j.title for j in mock_job_info_list],
        location=[j.location for j in mock_job_info_list],
        url=[j.url for j in mock_job_info_list],
        description=[j.description for j in mock_job_info_list],
    ))
