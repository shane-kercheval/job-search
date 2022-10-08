import os
from pytest_httpserver import HTTPServer
from bs4 import BeautifulSoup
import yaml


from source.jobs_scraper import JobInfo, JobScraperBase
from source.scrapers.vercel import VercelJobScraper
from source.scrapers.anaconda import AnacondaJobScraper
# from source.scrapers.chime_analytics import ChimeAnalyticsJobScraper


class VercelMockJobScraper(JobScraperBase):
    def __init__(self, url) -> None:
        super().__init__()
        self._url = url

    @property
    def url(self):
        return self._url

    def _extract_job_objects(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        job_objects = soup.select('a[class^=job-card_jobCard]')
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


def test_mock_vercel(httpserver: HTTPServer):
    ####
    # Set up mock server using html files in `vercel_clone`; I've copied the files locally so
    # we can test on local http-server. If the html ever changes on Vercel's website, consider
    # retaining the current function so that we have an example that is tested from local files.
    # The main advantage is that we can test changes more quickly (e.g. adding additional fields
    # to JobInfo object) compared with hitting external server each time.)
    ####
    def get_html(path: str) -> str:
        with open(path, 'r') as handle:
            return handle.read()
    # setup mock server for /careers page
    careers_html = get_html('tests/test_files/vercel_clone/vercel_careers_clone.html')
    httpserver.expect_request("/careers").respond_with_data(careers_html)
    # setup mock server for each of the job's pages
    jobs_path = 'tests/test_files/vercel_clone/careers'
    html_files = os.listdir(jobs_path)
    for file in html_files:
        job_html = get_html(os.path.join(jobs_path, file))
        mock_path = os.path.join("/careers", file.removesuffix('.html'))
        httpserver.expect_request(mock_path).respond_with_data(job_html)

    url = httpserver.url_for("/careers")
    scraper = VercelMockJobScraper(url)
    jobs = scraper.scrape()

    expected_titles = [
        'Analytics Engineer',
        'Application Security Engineer',
        'Content Engineer',
        'Customer Success Manager, APAC',
        'Customer Success Manager, Europe',
        'Data Engineer',
        'Data Engineer, Europe',
        'Data Scientist',
        'Director, Commercial Legal',
        'Director of Revenue Marketing',
        'Engineering Manager, Edge Network',
        'Engineering Manager, Turborepo',
        'Enterprise Account Executive, APAC',
        'Enterprise Account Executive, Europe',
        'Field Marketing Manager, West',
        'Financial Systems Analyst',
        'Head of Business Operations',
        'Infrastructure Engineer',
        'Instructional Designer, Europe',
        'Mid-Market Account Executive, APAC',
        'Mid-Market Account Executive, Europe',
        'Multimedia Designer',
        'Partner Manager, Services, APAC',
        'Partner Manager (Services), Europe',
        'Product Advocate',
        'Product Manager, Usage and Billing',
        'Sales Development Lead, APAC',
        'Sales Development Representative, Enterprise',
        'Sales Development Representative, Enterprise, Europe',
        'Sales Development Representative Manager, East',
        'Sales Development Representative, Mid Market',
        'Sales Engineer',
        'Sales Engineer, APAC',
        'Sales Engineer, Europe',
        'Salesforce Administrator',
        'Senior Manager, Customer Success Management',
        'Senior Manager, Trust and Safety',
        'Senior Marketing Operations Manager',
        'Senior Product Manager, Collaboration',
        'Senior Product Manager, Next.js, Europe',
        'Senior Product Manager, Turborepo',
        'Senior Visual Web Designer',
        'Software Engineer, Observability,  Europe',
        'Software Engineer, Support Tools',
        'Software Engineer, Systems',
        'Solutions Engineer',
        'Solutions Engineer, Europe',
        'Solutions Engineer, Partnerships',
        'Staff Software Engineer, Systems',
        'Technical Enablement Lead, Europe',
        'Technical Inbound Sales Lead, Europe',
        'Vercel General Application',
        'Vice President, GTM Operations',
        'Visual Designer, Brand Marketing'
    ]
    assert expected_titles == [x.title for x in jobs]

    expected_locations = [
        'United States, Canada',
        'United States',
        'United States',
        'Australia',
        'Germany, United Kingdom',
        'United States, Germany, United Kingdom',
        'United States, Germany, United Kingdom',
        'United States',
        'United States',
        'United States',
        'United States',
        'United States',
        'Australia',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'United States',
        'United States',
        'United States, United Kingdom',
        'Australia',
        'Germany, United Kingdom',
        'United States',
        'Australia',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'Australia',
        'United States',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'United States',
        'Australia',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'United States',
        'United States',
        'United States',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'Germany, United Kingdom',
        'United States, Germany, United Kingdom',
        'United States',
        'United States',
        'Germany, United Kingdom',
        'United States',
        'United States',
        'Germany, United Kingdom',
        'Germany, United Kingdom',
        'United States, Germany, United Kingdom',
        'United States',
        'United States'
    ]
    assert expected_locations == [x.location for x in jobs]

    expected_urls = [
        'http://127.0.0.1:8000/careers/analytics-engineer-amer-4486497004',
        'http://127.0.0.1:8000/careers/application-security-engineer-us-4626993004',
        'http://127.0.0.1:8000/careers/content-engineer-us-4534477004',
        'http://127.0.0.1:8000/careers/customer-success-manager-apac-4159182004',
        'http://127.0.0.1:8000/careers/customer-success-manager-europe-uk-4215448004',
        'http://127.0.0.1:8000/careers/data-engineer-uk-us-4664444004',
        'http://127.0.0.1:8000/careers/data-engineer-europe-uk-us-4674120004',
        'http://127.0.0.1:8000/careers/data-scientist-us-4554464004',
        'http://127.0.0.1:8000/careers/director-commercial-legal-us-4505262004',
        'http://127.0.0.1:8000/careers/director-of-revenue-marketing-us-4675158004',
        'http://127.0.0.1:8000/careers/engineering-manager-edge-network-us-4534415004',
        'http://127.0.0.1:8000/careers/engineering-manager-turborepo-us-4531844004',
        'http://127.0.0.1:8000/careers/enterprise-account-executive-apac-4346323004',
        'http://127.0.0.1:8000/careers/enterprise-account-executive-europe-uk-4235041004',
        'http://127.0.0.1:8000/careers/field-marketing-manager-west-us-4623565004',
        'http://127.0.0.1:8000/careers/financial-systems-analyst-us-4668362004',
        'http://127.0.0.1:8000/careers/head-of-business-operations-us-4657870004',
        'http://127.0.0.1:8000/careers/infrastructure-engineer-us-4159198004',
        'http://127.0.0.1:8000/careers/instructional-designer-europe-uk-us-4651728004',
        'http://127.0.0.1:8000/careers/mid-market-account-executive-apac-4466236004',
        'http://127.0.0.1:8000/careers/mid-market-account-executive-europe-uk-4180390004',
        'http://127.0.0.1:8000/careers/multimedia-designer-us-4677077004',
        'http://127.0.0.1:8000/careers/partner-manager-services-apac-4553099004',
        'http://127.0.0.1:8000/careers/partner-manager-services-europe-uk-4502534004',
        'http://127.0.0.1:8000/careers/product-advocate-us-4558502004',
        'http://127.0.0.1:8000/careers/product-manager-usage-and-billing-us-4327432004',
        'http://127.0.0.1:8000/careers/sales-development-lead-apac-4423850004',
        'http://127.0.0.1:8000/careers/sales-development-representative-enterprise-us-4586706004',
        'http://127.0.0.1:8000/careers/sales-development-representative-enterprise-europe-uk-4646256004',  # noqa
        'http://127.0.0.1:8000/careers/sales-development-representative-manager-east-us-4581381004',  # noqa
        'http://127.0.0.1:8000/careers/sales-development-representative-mid-market-us-4414553004',
        'http://127.0.0.1:8000/careers/sales-engineer-us-4162371004',
        'http://127.0.0.1:8000/careers/sales-engineer-apac-4159197004',
        'http://127.0.0.1:8000/careers/sales-engineer-europe-uk-4182467004',
        'http://127.0.0.1:8000/careers/salesforce-administrator-us-4606272004',
        'http://127.0.0.1:8000/careers/senior-manager-customer-success-management-us-4426201004',
        'http://127.0.0.1:8000/careers/senior-manager-trust-and-safety-us-4431286004',
        'http://127.0.0.1:8000/careers/senior-marketing-operations-manager-us-4625781004',
        'http://127.0.0.1:8000/careers/senior-product-manager-collaboration-us-4486791004',
        'http://127.0.0.1:8000/careers/senior-product-manager-next-js-europe-uk-4434286004',
        'http://127.0.0.1:8000/careers/senior-product-manager-turborepo-us-4547564004',
        'http://127.0.0.1:8000/careers/senior-visual-web-designer-us-4376536004',
        'http://127.0.0.1:8000/careers/software-engineer-observability-europe-uk-4531506004',
        'http://127.0.0.1:8000/careers/software-engineer-support-tools-uk-us-4641478004',
        'http://127.0.0.1:8000/careers/software-engineer-systems-us-4656326004',
        'http://127.0.0.1:8000/careers/solutions-engineer-us-4553561004',
        'http://127.0.0.1:8000/careers/solutions-engineer-europe-uk-4159200004',
        'http://127.0.0.1:8000/careers/solutions-engineer-partnerships-us-4553614004',
        'http://127.0.0.1:8000/careers/staff-software-engineer-systems-us-4652493004',
        'http://127.0.0.1:8000/careers/technical-enablement-lead-europe-uk-4598745004',
        'http://127.0.0.1:8000/careers/technical-inbound-sales-lead-europe-uk-4603098004',
        'http://127.0.0.1:8000/careers/vercel-general-application-uk-us-4569242004',
        'http://127.0.0.1:8000/careers/vice-president-gtm-operations-us-4436899004',
        'http://127.0.0.1:8000/careers/visual-designer-brand-marketing-us-4536670004'
    ]
    assert expected_urls == [x.url for x in jobs]
    assert all([x.description is not None for x in jobs])


def job_to_dict(job: JobInfo) -> list[dict]:
    return dict(
        title=job.title,
        location=job.location,
        url=job.url,
        description=job.description[0:20]
    )


def test_vercel():
    scraper = VercelJobScraper()
    jobs = scraper.scrape()
    assert len(jobs) > 0
    with open('tests/test_files/extracted_jobs/vercel_jobs.yml', 'w') as outfile:
        yaml.dump([job_to_dict(x) for x in jobs], outfile)


def test_anaconda():
    scraper = AnacondaJobScraper()
    jobs = scraper.scrape()
    assert len(jobs) > 0
    with open('tests/test_files/extracted_jobs/anaconda_jobs.yml', 'w') as outfile:
        yaml.dump([job_to_dict(x) for x in jobs], outfile)


# def test_chime_analytics():
#     scraper = ChimeAnalyticsJobScraper()
#     jobs = scraper.scrape()
#     assert len(jobs) > 0
#     with open('tests/test_files/extracted_jobs/chime_analytics_jobs.yml', 'w') as outfile:
#         yaml.dump([job_to_dict(x) for x in jobs], outfile)
