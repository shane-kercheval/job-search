from abc import ABC, abstractmethod
import source.domain.scrape as scrape
from source.entities.job_info import JobInfo


class JobScraperBase(ABC):
    """
    This base class provides the core logic to scrape a typical careers/job page, where each job
    listing is in an HTML element that can be selected via BeautifulSoup and each job HTML element
    contains a job title, location (optional), and a URL that references the job description.

    Child classes specify url and HTML selectors by overriddening the necessary properies. Then the
    class can be used as follows:

        scraper = CompanyXJobScraper()
        jobs = scraper.scrape()

    """
    @property
    @abstractmethod
    def company(self):
        """Returns the name of the company."""

    @property
    @abstractmethod
    def url(self):
        """Returns the URL to the careers/jobs page."""

    @abstractmethod
    def _extract_job_objects(self, html: str) -> list[str]:
        """Takes a string containg HTML of self.url and returns a list of html elements containing
        the job information (e.g. title, location, job description url)."""

    @abstractmethod
    def _extract_title(self, html: str) -> str:
        """
        Takes a string containing HTML of a job and extracts the job title.
        """

    @abstractmethod
    def _extract_location(self, html: str) -> str:
        """
        TBD
        """

    @abstractmethod
    def _extract_url(self, html: str) -> str:
        """
        TBD
        """
    @abstractmethod
    def _extract_job_description(self, html: str) -> str:
        """
        TBD
        """

    @property
    def job_objects_use_javascript(self):
        """
        If the site uses Javascript to load jobs (e.g. from external site / container) then we
        need to use requests_html.HTMLSession to load the entire site after rendering JavaScript;
        whereas requests.get will load the html before JavaScript runs and the page fully renders.

        Unsurprisingly, requests.get is much faster than requests_html.HTMLSession

        - Returning `False` from this property will use use requests.get
        - Returning `True` from this property will use use requests_html.HTMLSession
        """
        return False

    @property
    def job_descriptions_use_javascript(self):
        """
        If the job-description web-pages uses Javascript to load information (e.g. from external
        site / container) then we need to use requests_html.HTMLSession to load the entire site
        after rendering JavaScript; whereas requests.get will load the html before JavaScript runs
        and the page fully renders.

        Unsurprisingly, requests.get is much faster than requests_html.HTMLSession

        - Returning `False` from this property will use use requests.get
        - Returning `True` from this property will use use requests_html.HTMLSession
        """
        return False

    def _create_job_url(self, job_path: str) -> str:
        """
        This function returns the url to job description. It takes the job_path which is the url
        that was extracted from the individual job tag/element from BeautifulSoup.

        This function is needed because some urls returned are relative to the careers url e.g.
        "/job_123" and some urls are absolute "company.com/careers/job_123"; the latter is required
        to scrape the job description.

        The default implementation is to append the job_path to self.url, but this method can be
        overridden as necessary in child classes.
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

    def _scrape_job_objects(self) -> list[str]:
        """
        This function scrapes the careers/job page (self.url) and extracts and returns the job
        objects (i.e. Tags) returned from BeautifulSoup's .select function. This can be overridden
        by child classes if needed.
        """
        if self.job_objects_use_javascript:
            html = scrape.render(url=self.url)
        else:
            html = scrape.get(url=self.url)

        job_objects = self._extract_job_objects(html=html)
        assert len(job_objects) > 0
        return job_objects

    def _extract_job_info(self, html: str) -> JobInfo:
        """
        This function takes an individual job listing on the careers page (i.e. one of the
        objects in the list returned by _scrape_job_objects) and extracts the job information,
        returning a JobInfo object.
        """
        title = self._extract_title(html=html)
        location = self._extract_location(html=html)
        job_url = self._create_job_url(job_path=self._extract_url(html=html))

        return JobInfo(
            company=self.company,
            title=title,
            location=location,
            url=job_url,
            description=None  # we will get descriptions from each job page async
        )

    def _scape_job_descriptions(self, job_urls: list[str]) -> list[str]:
        """
        This method takes a list of urls that correspond to the job description from individual
        jobs, and scrapes each url, extracting the description, and returning a list of
        descriptions.
        """
        if self.job_descriptions_use_javascript:
            htmls = scrape.render(url=job_urls)
        else:
            htmls = scrape.get(url=job_urls)

        descriptions = [self._extract_job_description(html=html) for html in htmls]
        assert len(descriptions) > 0
        return descriptions

    def scrape(self) -> list[JobInfo]:
        """
        This function scrapes the job information from self.url and returns a list of JobInfo
        objects.
        """
        job_objects = self._scrape_job_objects()
        jobs = [self._extract_job_info(x) for x in job_objects]
        urls = [x.url for x in jobs]
        assert len(urls) == len(set(urls))  # ensure unique urls
        descriptions = self._scape_job_descriptions(job_urls=urls)
        for job, description in zip(jobs, descriptions):
            job.description = description

        self._assert_job_info_values(jobs)
        return jobs
