from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class JobInfo:
    title: str = None
    location: str = None
    url: str = None
    description: str = None


def scrape_vercel(url='https://vercel.com/careers') -> list[JobInfo]:
    """
    This function scrapes the job information from vercel.com and returns a list of JobInfo
    objects.
    """
    response_careers = requests.get(url=url)
    assert response_careers.status_code == 200

    soup_careers = BeautifulSoup(response_careers.text, 'html.parser')
    job_objects = soup_careers.select("a[class^=job-card_jobCard]")

    def create_job_url(job_path: str) -> str:
        return url + job_path.replace('/careers', '')

    def scrape_description(html: str) -> str:
        soup_desc = BeautifulSoup(html, 'html.parser')
        return str(soup_desc.select("section[class^=details_container]")[0].contents[0])

    def extract_job_info(tag: Tag) -> JobInfo:
        title = tag.select('h3')
        assert len(title) == 1
        location = tag.select('h4')
        assert len(location) == 1

        job_url = create_job_url(job_path=tag.attrs['href'].strip())
        resp = requests.get(url=job_url)
        assert resp.status_code == 200
        description = scrape_description(resp.text)

        return JobInfo(
            title=title[0].text.strip(),
            location=location[0].text.strip(),
            url=job_url,
            description=description
        )

    return [extract_job_info(x) for x in job_objects]
