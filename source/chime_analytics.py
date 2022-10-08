from source.jobs_scraper import JobScraperBase


class ChimeAnalyticsJobScraper(JobScraperBase):
    @property
    def url(self):
        return 'https://careers.chime.com/c/analytics-jobs'

    @property
    def uses_javascript(self):
        return True

    @property
    def job_objects_selector(self):
        return 'li.jobs-list-item'

    @property
    def title_selector(self):
        return 'a'

    @property
    def location_selector(self):
        return 'span.job-location'

    @property
    def job_description_selector(self):
        return 'section[class^=details_container]'

    def _create_job_url(self, job_path: str) -> str:
        return self.url + job_path.replace('/careers', '')
