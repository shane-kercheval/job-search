from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests


@dataclass
class Job:
    title: str
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
    def _scrape_jobs(self, html: str) -> tuple[str, str]:
        ...

    @abstractmethod
    def _scrape_description(self, html: str) -> str:
        ...

    def scrape(self) -> list[Job]:
        resp = requests.get(url=self.url)
        assert resp.status_code == 200
        jobs = self._scrape_jobs(resp.text)

        def get_scrape(url: str) -> str:
            resp = requests.get(url=url)
            assert resp.status_code == 200
            return self._scrape_description(resp.text)

        path_urls = [self._create_job_url(job_path) for _, job_path in jobs]
        assert len(jobs) == len(path_urls)
        jobs = [Job(title=j[0], url=p, description=get_scrape(p)) for j, p in zip(jobs, path_urls)]
        return jobs
