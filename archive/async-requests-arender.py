from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup


def extract_job_description(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    job_description = soup.select('section.job-description')
    assert len(job_description) == 1
    return job_description[0].text[0:100]


async def arender(session, url: str) -> str:
    """
    returns tuple including url and html (url is returned because asession.run does not seem to
    ensure the same order is returned)
    """
    r = await session.get(url=url)
    await r.html.arender()
    return url, r.html.html


def extract_descriptions(session, urls: list[str]) -> list[str]:
    assert len(urls) == len(set(urls))  # ensure unique urls
    # url=url explained in these links
    # https://stackoverflow.com/questions/67656204/how-can-i-build-a-list-of-async-tasks-with-argument-for-asynchtmlsession-run
    # https://docs.python.org/3.4/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
    # warning does not return in same order
    results = session.run(*[lambda url=url: arender(session, url) for url in urls])
    assert set(urls) == set(x[0] for x in results)
    # ensure we return the job descriptions in the same order of the urls passed in
    results = dict(results)  # keys are urls and values are
    return [extract_job_description(html=results[x]) for x in urls]


urls = [
    'https://careers.chime.com/job/6131676002/Senior-Data-Analyst-Corporate-Strategy',
    'https://careers.chime.com/job/6207420002/Lead-Data-Scientist-Marketing-Experimentation',
    'https://careers.chime.com/job/6289551002/Staff-Data-Analyst-Lifecycle-Marketing',
]
asession = AsyncHTMLSession()
print(extract_descriptions(asession, urls))

print('round 2')

asession = AsyncHTMLSession()
print(extract_descriptions(asession, urls))
