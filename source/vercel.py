from source.jobs_scraper import JobScraperBase


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
