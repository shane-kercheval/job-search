from functools import singledispatch
from collections.abc import Iterable
import requests
from requests_html import HTMLSession, AsyncHTMLSession

import asyncio
import aiohttp


class RequestException(Exception):
    pass


@singledispatch
def get(url) -> object:
    """
    This function scrapes the HTML from either a single url (if a single string is passed in) or a
    set of urls (asynchronously) if a list of strings are passed in.

    Specifically, `get` scrapes the HTML before any JavaScript has rendered (whereas the `render`
    function loads the Javascript and subsequently scrapes the HTML). `get` is faster and prefered
    when the HTML of interest isn't loaded from JavasScript.
    """
    raise ValueError(f'Type={type(url)}. Only values of type str or list[str] are permitted.')


@get.register(str)
def _(url: str) -> str:
    response = requests.get(url=url)
    assert response.status_code == 200
    return response.text


@get.register(Iterable[str])
def _(url: Iterable[str]) -> Iterable[str]:
    async def scrape_single(session, url):
        """This function takes the HTML from an web-page and extracts the HTML."""
        async with session.get(url) as resp:
            # resp.status_code????????
            html = await resp.text()
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


@singledispatch
def render(url) -> object:
    """
    This function scrapes the HTML from either a single url (if a single string is passed in) or a
    set of urls (asynchronously) if a list of strings are passed in.

    Specifically, `render` scrapes the HTML after any JavaScript has rendered (whereas the `get`
    function scrapes the HTML before any Javascript has rendered). `get` is faster and prefered
    when the HTML of interest isn't loaded from JavasScript.
    """
    raise ValueError(f'Type={type(url)}. Only values of type str or list[str] are permitted.')


@render.register(str)
def _(url: str) -> str:
    # https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with HTMLSession() as session:
        response = session.get(url=url)
        response.html.render(timeout=20)
        return response.html.html


@render.register(Iterable[str])
def _(url: Iterable[str]) -> list[str]:
    urls = url; del url  # noqa

    async def arender(session, url: str) -> str:
        """
        returns tuple including url and html (url is returned because asession.run does not seem to
        ensure the same order is returned)
        """
        r = await session.get(url=url)
        # r.status_code????
        await r.html.arender()
        return url, r.html.html

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
