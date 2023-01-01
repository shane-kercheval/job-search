from collections.abc import Iterable
import requests
from requests_html import HTMLSession, AsyncHTMLSession

import asyncio
import aiohttp


class RequestException(Exception):
    pass


def get(url) -> object:
    """
    This function scrapes the HTML from either a single url (if a single string is passed in) or a
    set of urls (asynchronously) if a list of strings are passed in.

    Specifically, `get` scrapes the HTML before any JavaScript has rendered (whereas the `render`
    function loads the Javascript and subsequently scrapes the HTML). `get` is faster and prefered
    when the HTML of interest isn't loaded from JavasScript.
    """
    if isinstance(url, str):
        response = requests.get(url=url)
        if response.status_code != 200:
            raise RequestException(f"status-code: {response.status_code}")
        return response.text
    elif isinstance(url, Iterable):
        async def scrape_single(session, url):
            """This function takes the HTML from an web-page and extracts the HTML."""
            async with session.get(url) as response:
                if response.status != 200:
                    raise RequestException(f"status-code: {response.status}")
                html = await response.text()
                return html

        async def get_results(urls):
            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in urls:
                    tasks.append(asyncio.ensure_future(scrape_single(session, url)))

                htmls = await asyncio.gather(*tasks)
                return htmls

        results = asyncio.run(get_results(urls=url))
        assert len(results) > 0
        return results
    else:
        raise ValueError(f'Type={type(url)}. Only values of type str or list[str] are permitted.')


def render(url: str, use_selenium: bool = False) -> str | list:
    """
    This function scrapes the HTML from either a single url (if a single string is passed in) or a
    set of urls (asynchronously) if a list of strings are passed in.

    Specifically, `render` scrapes the HTML after any JavaScript has rendered (whereas the `get`
    function scrapes the HTML before any Javascript has rendered). `get` is faster and prefered
    when the HTML of interest isn't loaded from JavasScript.

    TODO: implement Selenium asynchronously

    Args:
        url: the url to scrape
        use_selenium: in some cases, HTMLSessions fails to render JavaScript. I'm not sure why. But
            selenium seems to work, although it seems to be much slower. If possible, avoid using
            selenium. You also must have Chrome installed.

            Currently only an option when passing a single url.
    """
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if isinstance(url, str):
            if use_selenium:
                from selenium import webdriver  # noqa
                from selenium.webdriver.chrome.options import Options
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument("--disable-setuid-sandbox")
                # options.add_argument('--ignore-ssl-errors=yes')
                # options.add_argument('--ignore-certificate-errors')
                driver = webdriver.Chrome(chrome_options=options)
                driver.implicitly_wait(20)
                driver.get(url)
                html = driver.page_source
                return html
            else:
                with HTMLSession() as session:
                    response = session.get(url=url)
                    if response.status_code != 200:
                        raise RequestException(f"status-code: {response.status_code}")
                    response.html.render(timeout=90)
                    return response.html.html
        elif isinstance(url, Iterable):
            urls = url; del url  # noqa

            async def arender(session, url: str) -> str:
                """
                returns tuple including url and html (url is returned because asession.run does not
                seem to ensure the same order is returned)
                """
                response = await session.get(url=url)
                if response.status_code != 200:
                    raise RequestException(f"status-code: {response.status_code}")
                await response.html.arender(timeout=20)
                return url, response.html.html

            session = AsyncHTMLSession()
            assert len(urls) == len(set(urls))  # ensure unique urls
            # url=url explained in these links
            # https://stackoverflow.com/questions/67656204/how-can-i-build-a-list-of-async-tasks-with-argument-for-asynchtmlsession-run
            # https://docs.python.org/3.4/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
            # warning does not return in same order
            results = session.run(*[lambda url=url: arender(session, url) for url in urls])
            assert set(urls) == set(x[0] for x in results)
            # ensure we return the job descriptions in the same order of the urls passed in
            results = dict(results)  # keys are urls and values are
            results = [results[x] for x in urls]
            return results

        else:
            raise ValueError(
                f'Type={type(url)}. Only values of type str or list[str] are permitted.'
            )
