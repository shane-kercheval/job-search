import pytest
import os
from pytest_httpserver import HTTPServer


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
