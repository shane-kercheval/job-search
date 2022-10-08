from http.server import HTTPServer
from bs4 import BeautifulSoup
from tests.conftest import setup_mock_server
from source.scrape import get


def test_get_string(httpserver: HTTPServer):
    setup_mock_server(httpserver)
    url = httpserver.url_for("/careers/analytics-engineer-amer-4486497004")
    html = get(url)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.select('title')[0].text == 'Analytics Engineer  – Vercel'
