from source.jobs_scraper import JobScraperBase
from bs4 import BeautifulSoup


class AnacondaJobScraper(JobScraperBase):
    @property
    def url(self):
        return 'https://anaconda.com/careers'

    @property
    def uses_javascript(self):
        return True

    def _extract_job_objects(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        job_objects = soup.select('.career-listing-link')
        assert len(job_objects) > 0
        return [str(x) for x in job_objects]

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_object = soup.select('span.title')
        assert len(title_object) == 1
        return title_object[0].text.strip()

    def _extract_location(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        location_object = soup.select('span.location')
        assert len(location_object) == 1
        return location_object[0].text.strip()

    def _extract_url(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.select('a')
        assert len(tag) == 1
        return tag[0].attrs['href']

    def _extract_job_description(self, html: str) -> str:
        soup_desc = BeautifulSoup(html, 'html.parser')
        return str(soup_desc.select('div#main')[0])

    def _create_job_url(self, job_path: str) -> str:
        return job_path
