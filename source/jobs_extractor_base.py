from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests


@dataclass
class JobInfo:
    title: str = None
    location: str = None
    url: str = None
    description: str = None


class JobsScaperBase(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        ...

    def _create_job_url(self, job_path: str) -> str:
        """
        This function takes the job_path of an individual job (extracted from the HTML; which could
        be either a complete/absolute url, or could be a relative path from the corresponding jobs
        page, and returns the complete url to the specific job corresponding to job_path.
        """
        return self.url + job_path

    @abstractmethod
    def _scrape_job_infos(self, html: str) -> list[JobInfo]:
        """
        This function takes the HTML from the jobs/career page (which has >=1 job posting) and
        extracts the job information and returns a list of Job objects.

        Args:
            html:
                the HTML extracted from the corresponding careers/jobs page for the corresponding
                company.
        """
        ...

    # @abstractmethod
    # def _scrape_description(self, html: str) -> str:
    #     """
    #     This function takes the HTML from a web-page corresponding to an individual job listing
    #     and extracts the applicable HTML specific to the job description.
    #     """
    #     ...

    def scrape(self) -> list[JobInfo]:
        """
        This function scapes the page of careers from self.url and all corresponding job listings.
        """
        resp = requests.get(url=self.url)
        assert resp.status_code == 200
        jobs = self._scrape_job_infos(resp.text)
        return jobs
