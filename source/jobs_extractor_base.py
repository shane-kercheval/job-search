from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests


@dataclass
class Job:
    title: str
    location: str
    url: str
    description: str


class JobsScaperBase(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        ...

    def _create_job_url(self, job_path: str) -> str:
        return self.url + job_path

    @abstractmethod
    def _scrape_job_infos(self, html: str) -> tuple[str, str, str]:
        """
        This function takes the HTML from the jobs/career page (which has >=1 job posting) and
        extracts the following for each job.
            - job title
            - location if applicable; if no location indicated, returns None
            - url for the job
        
        Args:
            html:
                the HTML extracted from the corresponding careers/jobs page for the corresponding
                company.
        """
        ...

    @abstractmethod
    def _scrape_description(self, html: str) -> str:
        """
        This function takes the HTML from a web-page corresponding to an individual job listing
        and extracts the applicable HTML specific to the job description.
        """
        ...

    def scrape(self) -> list[Job]:
        """
        This function scapes the page of careers from self.url and all corresponding job listings.
        """
        resp = requests.get(url=self.url)
        assert resp.status_code == 200
        jobs = self._scrape_job_infos(resp.text)

        def get_scrape(url: str) -> str:
            resp = requests.get(url=url)
            assert resp.status_code == 200
            return self._scrape_description(resp.text)

        path_urls = [self._create_job_url(job_path) for _, _, job_path in jobs]
        assert len(jobs) == len(path_urls)
        jobs = [
            Job(title=j[0], location=j[1], url=p, description=get_scrape(p))
            for j, p in zip(jobs, path_urls)
        ]
        return jobs
