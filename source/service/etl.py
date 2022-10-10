from helpsk.database import Sqlite

from source.service.database import save_job_infos, datetime_now_utc
from source.domain.scrapers import AnacondaJobScraper, ChimeAnalyticsJobScraper, VercelJobScraper

scrapers = [
    AnacondaJobScraper(),
    ChimeAnalyticsJobScraper(),
    VercelJobScraper()
]

snapshot = datetime_now_utc()
db = Sqlite('data/jobs.db')

for scraper in scrapers:
    jobs = scraper.scrape()
    print(f'{scraper.company}: {len(jobs)}')
    save_job_infos(
        database=db,
        jobs=jobs,
        snapshot=snapshot
    )
