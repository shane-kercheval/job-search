import pytest
from http.server import HTTPServer
from bs4 import BeautifulSoup
from tests.conftest import setup_mock_server
from source.domain.scrape import RequestException, get, render


def test_get_type_not_supported():
    with pytest.raises(ValueError):
        get(1)


def test_get_type_not_supported_none():
    with pytest.raises(ValueError):
        get(None)


def test_render_type_not_supported():
    with pytest.raises(ValueError):
        render(1)


def test_render_type_not_supported_none():
    with pytest.raises(ValueError):
        render(None)


def test_get_single_url_status_not_200(httpserver: HTTPServer):
    with pytest.raises(RequestException):
        setup_mock_server(httpserver)
        url = httpserver.url_for('/invalid')
        get(url)


def test_get_multiple_urls_status_not_200(httpserver: HTTPServer):
    with pytest.raises(RequestException):
        setup_mock_server(httpserver)
        get(url=[httpserver.url_for(x) for x in ['/invalid', '/invalid']])


def test_render_single_url_status_not_200(httpserver: HTTPServer):
    with pytest.raises(RequestException):
        setup_mock_server(httpserver)
        url = httpserver.url_for('/invalid')
        render(url)


def test_render_multiple_urls_status_not_200(httpserver: HTTPServer):
    with pytest.raises(RequestException):
        setup_mock_server(httpserver)
        render(url=[httpserver.url_for(x) for x in ['/invalid1', '/invalid2']])


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


def test_render_single_url(httpserver: HTTPServer):
    setup_mock_server(httpserver)
    url = httpserver.url_for('/careers/analytics-engineer-amer-4486497004')
    html = render(url)
    assert 'Analytics Engineer  – Vercel' in html


def test_render_multiple_urls(httpserver: HTTPServer):
    setup_mock_server(httpserver)
    urls = [
        '/careers/analytics-engineer-amer-4486497004',
        '/careers/field-marketing-manager-west-us-4623565004',
        '/careers/senior-manager-customer-success-management-us-4426201004',
        '/careers/instructional-designer-europe-uk-us-4651728004',
    ]
    urls = [httpserver.url_for(url) for url in urls]
    htmls = render(urls)
    assert len(htmls) == len(urls)

    assert 'Analytics Engineer  – Vercel' in htmls[0]
    assert 'Field Marketing Manager, West – Vercel' in htmls[1]
    assert 'Senior Manager, Customer Success Management – Vercel' in htmls[2]
    assert 'Instructional Designer, Europe – Vercel' in htmls[3]
