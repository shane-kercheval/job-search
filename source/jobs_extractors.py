from source.jobs_extractor_base import JobsScaperBase, Job


class VercelJobsExtractor(JobsScaperBase):
    @property
    def url(self) -> str:
        return 'https://vercel.com/careers'

    def _create_job_url(self, job_path: str) -> str:
        return self.url + job_path.replace('/careers', '')

    def _scrape_job_infos(self, html: str) -> tuple[str, str]:
        """
        Given the html of the vercel careers page, extract the title and url of associated job.
        """
        from bs4 import BeautifulSoup
        from bs4.element import Tag

        soup = BeautifulSoup(html, 'html.parser')
        jobs = soup.select("a[class^=job-card_jobCard]")

        def extract_title_url(tag: Tag):
            title = tag.select('h3')
            assert len(title) == 1
            url = tag.attrs['href']
            return title[0].text.strip(), url.strip()

        titles_urls = [extract_title_url(x) for x in jobs]
        return titles_urls

    def _scrape_description(self, html: str) -> list[Job]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        return str(soup.select("section[class^=details_container]")[0].contents[0])
