from helpsk.database import Sqlite

from source.domain.scrapers import AnacondaJobScraper, ChimeAnalyticsJobScraper, \
    ChimeDataScienceJobScraper, VercelJobScraper
from source.service.database import save_job_infos, datetime_now_utc


def main():
    scrapers = [
        AnacondaJobScraper(),
        ChimeAnalyticsJobScraper(),
        ChimeDataScienceJobScraper(),
        VercelJobScraper()
    ]

    snapshot = datetime_now_utc()
    db = Sqlite(path='data/jobs.db')

    for scraper in scrapers:
        print(f'Scraping {scraper.company} ...')
        jobs = scraper.scrape()
        print(f'Scraped {scraper.company}: {len(jobs)}')
        save_job_infos(
            database=db,
            jobs=jobs,
            snapshot=snapshot
        )


if __name__ == '__main__':
    main()
