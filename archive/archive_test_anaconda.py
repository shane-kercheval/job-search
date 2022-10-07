from source.anaconda import AnacondaJobScraper
from source.vercel import VercelJobScraper


def test_anaconda():
    import time
    start = time.time()
    scraper = AnacondaJobScraper()
    jobs = scraper.scrape()

    end = time.time()
    print(end - start)
    for job in jobs:
        print(job.title)
    assert len(jobs) > 0


def test_vercel():
    import time
    start = time.time()
    scraper = VercelJobScraper()
    jobs = scraper.scrape()
    end = time.time()
    print(end - start)
    for job in jobs:
        print(job.title)
    assert len(jobs) > 0


if __name__ == '__main__':
    test_vercel()
    test_anaconda()
    test_anaconda()
    test_vercel()
