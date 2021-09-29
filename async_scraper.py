from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import Future
import requests
import time
from bs4 import BeautifulSoup


class AsyncScraper:
    def __init__(self, urls, pool_type, workers=4, display_time=False, display_progress=False):
        self.urls = urls                            # list of urls
        self.pool_type = pool_type                  # threads or processes
        self.workers = workers                      # number of workers
        self.display_time = display_time            # total time
        self.display_progress = display_progress

    def scrape_one(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            if self.display_progress == True:
                print(f"scraped: {url}")
            return r.content

    def execute(self):

        results = []

        if self.pool_type == "processes":
            with ProcessPoolExecutor(max_workers=self.workers) as executor:
                if self.display_time == True:
                    start_time = time.time()
                futures = [executor.submit(self.scrape_one, url)
                           for url in self.urls]

        elif self.pool_type == "threads":
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                if self.display_time == True:
                    start_time = time.time()
                futures = [executor.submit(self.scrape_one, url)
                           for url in self.urls]

        else:
            print("invalid pool_type")
            return

        for future in futures:
            results.append(future.result())

        if self.display_time == True:
            end_time = time.time()
            print(f"total time: {end_time-start_time}")

        return results

# this would change
# do whatever ya gotta do to generate list of urls
def url_generator(date, pages):
    base_url = f"https://websitebiography.com/new_domain_registrations/{date}"
    return [f"{base_url}/{i}" for i in range(1, pages+1)]

urls = url_generator("2021-08-31", 87)

# then scrape
scraper = AsyncScraper(urls=urls, pool_type="processes",
                       workers=4, display_progress=True, display_time=True)

results = scraper.execute()
