from source.domain.jobs_scraper import JobScraperBase
from bs4 import BeautifulSoup


class VercelJobScraper(JobScraperBase):
    @property
    def company(self):
        return 'Vercel'

    @property
    def url(self):
        return 'https://vercel.com/careers'

    def _extract_job_objects(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        job_objects = soup.select('a[class^=job-card_]')
        assert len(job_objects) > 0
        return [str(x) for x in job_objects]

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_object = soup.select('h3')
        assert len(title_object) == 1
        return title_object[0].text.strip()

    def _extract_location(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        location_object = soup.select('h4')
        assert len(location_object) == 1
        return location_object[0].text.strip()

    def _extract_url(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.select('a')
        assert len(tag) == 1
        return tag[0].attrs['href']

    def _extract_job_description(self, html: str) -> str:
        soup_desc = BeautifulSoup(html, 'html.parser')
        return str(soup_desc.select('section[class^=details_container]')[0])

    def _create_job_url(self, job_path: str) -> str:
        return self.url + job_path.replace('/careers', '')


class AnacondaJobScraper(JobScraperBase):
    @property
    def company(self):
        return 'Anaconda'

    @property
    def url(self):
        return 'https://anaconda.com/careers'

    @property
    def job_objects_use_javascript(self):
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


class ChimeJobScraper(JobScraperBase):

    @property
    def job_objects_use_javascript(self):
        return True

    @property
    def job_descriptions_use_javascript(self):
        return True

    def _extract_job_objects(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        job_objects = soup.select('li.jobs-list-item')
        assert len(job_objects) > 0
        return [str(x) for x in job_objects]

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_object = soup.select('a')
        assert len(title_object) == 1
        return title_object[0].text.strip()

    def _extract_location(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        location_object = soup.select('span.job-location')
        assert len(location_object) == 1
        temp = location_object[0].text.strip().split('\n')
        return temp[-1].strip()

    def _extract_url(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.select('a')
        assert len(tag) == 1
        return tag[0].attrs['href']

    def _extract_job_description(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        return str(soup.select('section[class^=job-description]')[0])

    def _create_job_url(self, job_path: str) -> str:
        return job_path


class ChimeAnalyticsJobScraper(ChimeJobScraper):
    @property
    def company(self):
        return 'Chime (Analytics)'

    @property
    def url(self):
        return 'https://careers.chime.com/c/analytics-jobs'


class ChimeDataScienceJobScraper(ChimeJobScraper):
    @property
    def company(self):
        return 'Chime (DS & ML)'

    @property
    def url(self):
        return 'https://careers.chime.com/c/data-science-machine-learning-jobs'


class OtterAIJobScraper(JobScraperBase):
    @property
    def company(self):
        return 'Otter AI'

    @property
    def url(self):
        return 'https://otter.ai/careers'

    @property
    def job_objects_use_javascript(self):
        return True

    @property
    def job_objects_use_selenium(self):
        return True

    @property
    def job_descriptions_use_javascript(self):
        return True

    @property
    def job_descriptions_use_selenium(self):
        return True

    def _extract_job_objects(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        # job_objects = soup.select('.career__position')
        job_objects = soup.select('a[class^=career__position-item]')
        assert len(job_objects) > 0
        return [str(x) for x in job_objects]

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_object = soup.find('div', class_='text-md cc-semi')
        assert len(title_object) == 1
        return title_object.text.strip()

    def _extract_location(self, html: str) -> str:
        return 'Location Not in Job Object'
        # soup = BeautifulSoup(html, 'html.parser')
        # location_object = soup.select('span.location')
        # assert len(location_object) == 1
        # return location_object[0].text.strip()

    def _extract_url(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        url = soup.find('a').get('href')
        assert len(url) > 0
        return url

    def _extract_job_description(self, html: str) -> str:
        # soup_desc = BeautifulSoup(html, 'html.parser')
        # return str(soup_desc.select('div#main')[0])
        return "Not Supported Yet"

    def _create_job_url(self, job_path: str) -> str:
        return job_path
