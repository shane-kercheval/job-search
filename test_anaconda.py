from source.anaconda import AnacondaJobScraper
from source.vercel import VercelJobScraper

from requests_html import HTMLSession

def test_anaconda():
    import time
    import logging
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
    import logging
    start = time.time()
    scraper = VercelJobScraper()
    jobs = scraper.scrape()
    end = time.time()
    logging.info(end - start)
    assert len(jobs) > 0


if __name__ == '__main__':
    # test_vercel()
    # test_vercel()
    # test_vercel()
    test_anaconda()
    test_anaconda()
    # with HTMLSession() as session:
    #     response_careers = session.get("https://anaconda.com/careers")
    #     response_careers.html.render(timeout=20)
    #     html = response_careers.html.html
    #     print(html[0:100])
        
    # with HTMLSession() as session:
    #     response_careers = session.get("https://anaconda.com/careers")
    #     response_careers.html.render(timeout=20)
    #     html = response_careers.html.html
    #     print(html[0:100])
