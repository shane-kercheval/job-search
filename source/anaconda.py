from source.jobs_scraper import JobScraperBase


class AnacondaJobScraper(JobScraperBase):

    @property
    def url(self):
        return 'https://anaconda.com/careers'

    @property
    def uses_javascript(self):
        return True

    @property
    def job_objects_selector(self):
        return '.career-listing-link'

    @property
    def job_description_selector(self):
        return 'div#main'

    @property
    def title_selector(self):
        return 'span.title'

    @property
    def location_selector(self):
        return 'span.location'

    def _create_job_url(self, job_path: str) -> str:
        return job_path
