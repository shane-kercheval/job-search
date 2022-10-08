from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

asession = AsyncHTMLSession()

urls = [
    'https://careers.chime.com/job/6131676002/Senior-Data-Analyst-Corporate-Strategy',
    'https://careers.chime.com/job/6207420002/Lead-Data-Scientist-Marketing-Experimentation',
    'https://careers.chime.com/job/6289551002/Staff-Data-Analyst-Lifecycle-Marketing',
]


def extract_job_description(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    job_description = soup.select('section.job-description')
    assert len(job_description) == 1
    return job_description[0].text[0:100]


async def extract_javascript(url):
    r = await asession.get(url=url)
    await r.html.arender()
    return extract_job_description(html=r.html.html)


# warning does not return in same order
result = asession.run(*[lambda: extract_javascript(url) for url in urls])
print(result)
