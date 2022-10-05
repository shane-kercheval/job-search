from source.jobs_page import JobsPage
import pytest
import requests

from pytest_httpserver import HTTPServer


# specify where the server should bind to
# you can return 0 as the port, in this case it will bind to a free (ephemeral) TCP port
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


# specify httpserver fixture
def test_oneshot_and_permanent_happy_path1(httpserver: HTTPServer):
    # define some request handlers
    # more details in the documentation
    httpserver.expect_request("/permanent").respond_with_data("OK permanent")
    httpserver.expect_oneshot_request("/oneshot1").respond_with_data("OK oneshot1")
    httpserver.expect_oneshot_request("/oneshot2").respond_with_data("OK oneshot2")

    # query those handlers with a real HTTP client (requests in this example but could by anything)
    # the 'url_for' method  formats the final URL, so there's no need to wire-in any ports
    assert requests.get(httpserver.url_for("/permanent")).text == "OK permanent"
    assert requests.get(httpserver.url_for("/oneshot1")).text == "OK oneshot1"

def test_vercel():
    page = JobsPage(
        url = 'https://vercel.com/careers',
        jobs_parser=None
    )
    assert page is not None
