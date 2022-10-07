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

    @property
    @abstractmethod
    def job_objects_selector(self):
        """CSS selector that results in a collection of jobs."""

    @property
    @abstractmethod
    def job_description_selector(self):
        """TBD"""

    @property
    @abstractmethod
    def title_selector(self):
        """TBD"""

    @property
    @abstractmethod
    def location_selector(self):
        """TBD"""

    @property
    def uses_javascript(self):
        """
        If the site uses Javascript to load jobs (e.g. from external site / container) then we
        need to use requests_html.HTMLSession to load the entire site after rendering JavaScript;
        whereas requests.get will load the html before JavaScript runs and the page fully renders.

        Unsurprisingly, requests.get is much faster than requests_html.HTMLSession

        - Returning `False` from this property will use use requests.get
        - Returning `True` from this property will use use requests_html.HTMLSession
        """
        return False

    def _create_job_url(self, job_path: str) -> str:
        """
        TBD
        """
        return self.url + job_path

    def _assert_job_info_values(self, jobs: list[JobInfo]) -> None:
        """
        Ensures that all JobInfo fields have values. This can be overridden by child classes in the
        case where we don't expect certain values (e.g. some jobs may not have location).
        """
        for job in jobs:
            assert job.title
            assert job.location
            assert job.title
            assert job.description

    def _scrape_job_objects(self) -> list[Tag]:
        """
        This function scrapes the careers/job page (self.url) and extracts and returns the job
        objects (i.e. Tags) returned from BeautifulSoup's .select function. This can be overridden
        by child classes if needed.
        """
        if self.uses_javascript:
            # https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            with HTMLSession() as session:
                response_careers = session.get(self.url)
                response_careers.html.render(timeout=20)
                html = response_careers.html.html
        else:
            response_careers = requests.get(url=self.url)
            assert response_careers.status_code == 200
            html = response_careers.text

        print('DONE HTMLSESSION')
        soup_careers = BeautifulSoup(html, 'html.parser')
        job_objects = soup_careers.select(self.job_objects_selector)
        assert len(job_objects) > 0

        return job_objects

    def _extract_job_info(self, job_object: Tag) -> JobInfo:
        """
        This function takes an individual job listing on the careers page (i.e. one of the
        objects in the list returned by _scrape_job_objects) and extracts the job information,
        returning a JobInfo object.
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

    def _scape_job_descriptions(self, job_urls):
        """
        """
        async def scrape_description_async(session, url):
            """
            This function takes the HTML from an individual job web-page and extracts the HTML that
            associated with the job description. The HTML is retained.
            """
            async with session.get(url) as resp:
                html = await resp.text()
                'Sr. Software Engineer' in html
                soup_desc = BeautifulSoup(html, 'html.parser')
                return str(soup_desc.select(self.job_description_selector)[0])

        async def get_descriptions(urls):
            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in urls:
                    tasks.append(asyncio.ensure_future(scrape_description_async(session, url)))

                job_htmls = await asyncio.gather(*tasks)
                return job_htmls

        descriptions = asyncio.run(get_descriptions(urls=job_urls))
        assert len(descriptions) > 0
        return descriptions

    def scrape(self) -> list[JobInfo]:
        """
        This function scrapes the job information from self.url and returns a list of JobInfo
        objects.
        """
        job_objects = self._scrape_job_objects()
        jobs = [self._extract_job_info(x) for x in job_objects]

        descriptions = self._scape_job_descriptions(job_urls=[x.url for x in jobs])
        for job, description in zip(jobs, descriptions):
            job.description = description

        self._assert_job_info_values(jobs)
        return jobs
