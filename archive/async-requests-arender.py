from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

asession = AsyncHTMLSession()


def extract_job_description(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    job_description = soup.select('section.job-description')
    assert len(job_description) == 1
    return job_description[0].text[0:100]


async def get_pythonorg():
    r = await asession.get('https://careers.chime.com/job/6131676002/Senior-Data-Analyst-Corporate-Strategy')
    await r.html.arender()
    return extract_job_description(html=r.html.html)


async def get_reddit():
    r = await asession.get('https://careers.chime.com/job/6207420002/Lead-Data-Scientist-Marketing-Experimentation')
    await r.html.arender()
    return extract_job_description(html=r.html.html)


async def get_google():
    r = await asession.get('https://careers.chime.com/job/6289551002/Staff-Data-Analyst-Lifecycle-Marketing')
    await r.html.arender()
    return extract_job_description(html=r.html.html)

result = asession.run(get_pythonorg, get_reddit, get_google)
print(result)
