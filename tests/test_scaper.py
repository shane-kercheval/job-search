from http.server import HTTPServer
from bs4 import BeautifulSoup
from tests.conftest import setup_mock_server
from source.scrape import get


def test_get_single_url(httpserver: HTTPServer):
    setup_mock_server(httpserver)
    url = httpserver.url_for('/careers/analytics-engineer-amer-4486497004')
    html = get(url)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.select('title')[0].text == 'Analytics Engineer  – Vercel'


def test_get_multiple_urls(httpserver: HTTPServer):
    setup_mock_server(httpserver)
    urls = [
        '/careers/analytics-engineer-amer-4486497004',
        '/careers/field-marketing-manager-west-us-4623565004',
        '/careers/senior-manager-customer-success-management-us-4426201004',
        '/careers/instructional-designer-europe-uk-us-4651728004',
    ]
    urls = [httpserver.url_for(url) for url in urls]
    htmls = get(urls)
    assert len(htmls) == len(urls)

    soup = BeautifulSoup(htmls[0], 'html.parser')
    assert soup.select('title')[0].text == 'Analytics Engineer  – Vercel'

    soup = BeautifulSoup(htmls[1], 'html.parser')
    assert soup.select('title')[0].text == 'Field Marketing Manager, West – Vercel'

    soup = BeautifulSoup(htmls[2], 'html.parser')
    assert soup.select('title')[0].text == 'Senior Manager, Customer Success Management – Vercel'

    soup = BeautifulSoup(htmls[3], 'html.parser')
    assert soup.select('title')[0].text == 'Instructional Designer, Europe – Vercel'
