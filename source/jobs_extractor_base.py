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
        """
        This function takes the value of the link in an job on the `/careers` page (e.g.
        `/careers/job_1`) and returns the absolute url (e.g. `https://vercel.com/careers/job_1`)
        """
        return url + job_path.replace('/careers', '')

    def scrape_description(html: str) -> str:
        """
        This function takes the HTML from an individual job web-page and extracts the HTML that
        associated with the job description. The HTML is retained.
        """
        soup_desc = BeautifulSoup(html, 'html.parser')
        return str(soup_desc.select("section[class^=details_container]")[0].contents[0])

    def extract_job_info(job_object: Tag) -> JobInfo:
        """
        This function takes an individual job listing on the careers page and extracts the
        information, returning a JobInfo object.
        """
        title = job_object.select('h3')
        assert len(title) == 1
        location = job_object.select('h4')
        assert len(location) == 1
        job_url = create_job_url(job_path=job_object.attrs['href'].strip())
        resp = requests.get(url=job_url)
        assert resp.status_code == 200
        description = scrape_description(resp.text)
        assert description is not None and description != ''

        return JobInfo(
            title=title[0].text.strip(),
            location=location[0].text.strip(),
            url=job_url,
            description=description
        )

    return [extract_job_info(x) for x in job_objects]
