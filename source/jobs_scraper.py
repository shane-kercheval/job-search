from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from requests_html import HTMLSession

import aiohttp
import asyncio


@dataclass
class JobInfo:
    title: str = None
    location: str = None
    url: str = None
    description: str = None


# extract collection of jobs from careers page
# for each job, get title, job url, job location (this might be in the job url not the collection
# of jobs)
# for all job urls, get description async
# perhaps we should get job locations last, and pass in both the job objects and the descriptions
# and it can extract from one of those.

# search in description text matches for keywords e.g. python, snowflake, etc.
# match resume to job description

class JobScraperBase(ABC):
    @property
    @abstractmethod
    def url(self):
        """Returns the URL to the careers/jobs page."""
        ...

    @property
    @abstractmethod
    def job_objects_selector(self):
        """CSS selector that results in a collection of jobs."""
        ...

    @property
    @abstractmethod
    def job_description_selector(self):
        """TBD"""
        ...

    @property
    @abstractmethod
    def title_selector(self):
        """TBD"""
        ...

    @property
    @abstractmethod
    def location_selector(self):
        """TBD"""
        ...

    @property
    def uses_javascript(self):
        return False

    def _create_job_url(self, job_path: str) -> str:
        """
        TBD
        """
        return self.url + job_path

    def scrape(self) -> list[JobInfo]:
        """
        This function scrapes the job information from vercel.com and returns a list of JobInfo
        objects.
        """
        if self.uses_javascript:
            with HTMLSession() as session:
                response_careers = session.get(self.url)
                response_careers.html.render(timeout=20)
                html = response_careers.html.html
        else:
            response_careers = requests.get(url=self.url)
            assert response_careers.status_code == 200
            html = response_careers.text

        soup_careers = BeautifulSoup(html, 'html.parser')
        job_objects = soup_careers.select(self.job_objects_selector)
        assert len(job_objects) > 0

        def extract_job_info(job_object: Tag) -> JobInfo:
            """
            This function takes an individual job listing on the careers page and extracts the
            information, returning a JobInfo object.
            """
            title = job_object.select(self.title_selector)
            assert len(title) == 1
            location = job_object.select(self.location_selector)
            assert len(location) == 1
            job_url = self._create_job_url(job_path=job_object.attrs['href'].strip())

            # description = scrape_description(job_url=job_url)
            # assert description is not None and description != ''

            return JobInfo(
                title=title[0].text.strip(),
                location=location[0].text.strip(),
                url=job_url,
                description=None  # we will get descriptions from each job page async
            )

        jobs = [extract_job_info(x) for x in job_objects]
        job_urls = [x.url for x in jobs]

        async def scrape_description_async(session, job_url):
            """
            This function takes the HTML from an individual job web-page and extracts the HTML that
            associated with the job description. The HTML is retained.
            """
            async with session.get(job_url) as resp:
                html = await resp.text()
                'Sr. Software Engineer' in html
                soup_desc = BeautifulSoup(html, 'html.parser')
                return str(soup_desc.select(self.job_description_selector)[0])

        async def get_descriptions():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in job_urls:
                    tasks.append(asyncio.ensure_future(scrape_description_async(session, url)))

                job_htmls = await asyncio.gather(*tasks)
                return job_htmls

        descriptions = asyncio.run(get_descriptions())
        assert len(descriptions) > 0

        for job, description in zip(jobs, descriptions):
            job.description = description

        return jobs
