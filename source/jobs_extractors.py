from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

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
        response_careers = requests.get(url=self.url)
        assert response_careers.status_code == 200

        soup_careers = BeautifulSoup(response_careers.text, 'html.parser')
        job_objects = soup_careers.select(self.job_objects_selector)

        async def scrape_description_async(session, job_url):
            """
            This function takes the HTML from an individual job web-page and extracts the HTML that
            associated with the job description. The HTML is retained.
            """
            async with session.get(job_url) as resp:
                html = await resp.text()
                soup_desc = BeautifulSoup(html, 'html.parser')
                return str(soup_desc.select(self.job_description_selector)[0].contents[0])

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


class VercelJobScraper(JobScraperBase):
    @property
    def url(self):
        return 'https://vercel.com/careers'

    @property
    def job_objects_selector(self):
        return 'a[class^=job-card_jobCard]'

    @property
    def job_description_selector(self):
        return 'section[class^=details_container]'

    @property
    def title_selector(self):
        return 'h3'

    @property
    def location_selector(self):
        return 'h4'

    def _create_job_url(self, job_path: str) -> str:
        return self.url + job_path.replace('/careers', '')


# def scrape_vercel(url='https://vercel.com/careers') -> list[JobInfo]:
#     """
#     This function scrapes the job information from vercel.com and returns a list of JobInfo
#     objects.
#     """
#     response_careers = requests.get(url=url)
#     assert response_careers.status_code == 200

#     soup_careers = BeautifulSoup(response_careers.text, 'html.parser')
#     job_objects = soup_careers.select("a[class^=job-card_jobCard]")

#     def create_job_url(job_path: str) -> str:
#         """
#         This function takes the value of the link in an job on the `/careers` page (e.g.
#         `/careers/job_1`) and returns the absolute url (e.g. `https://vercel.com/careers/job_1`)
#         """
#         return url + job_path.replace('/careers', '')

#     def scrape_description(job_url: str) -> str:
#         """
#         This function takes the HTML from an individual job web-page and extracts the HTML that
#         associated with the job description. The HTML is retained.
#         """
#         resp = requests.get(url=job_url)
#         assert resp.status_code == 200
#         soup_desc = BeautifulSoup(resp.text, 'html.parser')
#         return str(soup_desc.select("section[class^=details_container]")[0].contents[0])

#     async def scrape_description_async(session, job_url):
#         """
#         This function takes the HTML from an individual job web-page and extracts the HTML that
#         associated with the job description. The HTML is retained.
#         """
#         async with session.get(job_url) as resp:
#             html = await resp.text()
#             soup_desc = BeautifulSoup(html, 'html.parser')
#             return str(soup_desc.select("section[class^=details_container]")[0].contents[0])

#     def extract_job_info(job_object: Tag) -> JobInfo:
#         """
#         This function takes an individual job listing on the careers page and extracts the
#         information, returning a JobInfo object.
#         """
#         title = job_object.select('h3')
#         assert len(title) == 1
#         location = job_object.select('h4')
#         assert len(location) == 1
#         job_url = create_job_url(job_path=job_object.attrs['href'].strip())

#         # description = scrape_description(job_url=job_url)
#         # assert description is not None and description != ''

#         return JobInfo(
#             title=title[0].text.strip(),
#             location=location[0].text.strip(),
#             url=job_url,
#             description=None  # we will get descriptions from each job page async
#         )

#     jobs = [extract_job_info(x) for x in job_objects]
#     job_urls = [x.url for x in jobs]

#     async def get_descriptions():
#         async with aiohttp.ClientSession() as session:
#             tasks = []
#             for url in job_urls:
#                 tasks.append(asyncio.ensure_future(scrape_description_async(session, url)))

#             job_htmls = await asyncio.gather(*tasks)
#             return job_htmls

#     descriptions = asyncio.run(get_descriptions())

#     #descriptions = [scrape_description(x) for x in job_urls]

#     assert len(descriptions) > 0

#     for job, description in zip(jobs, descriptions):
#         job.description = description

#     return jobs
