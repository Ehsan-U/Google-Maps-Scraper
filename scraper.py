import csv
from playwright.sync_api import sync_playwright
from time import sleep
from rich.console import Console
import argparse
from unidecode import unidecode

class Google():

    def __init__(self, url, limit):
        self.url = url
        self.limit = limit
        self.play = sync_playwright().start()
        self.browser = self.play.chromium.launch(headless=False, slow_mo=50)
        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width":1280,"height":720})
        self.records = 0
        self.con = Console()
        self.all_items = []


    def initiate(self):
        self.page.goto(self.url)
        while self.records < self.limit:
            goto = self.page.locator("//div[@data-review-id and @jsaction]/div[3]").last
            names = self.page.locator("//div[@data-review-id and @jsaction]/div[3]/div[@jsan]/div[@style]/div[1]/a/div[1]/span")
            reviews = self.page.locator("//div[@data-review-id and @jsaction]/div[3]/div[last()]/div[@id]/span[@class]")
            items = []
            for name,review in zip(names.element_handles()[self.records:], reviews.element_handles()[self.records:]):
                self.records +=1
                item = [
                    unidecode(name.text_content()),
                    unidecode(review.text_content())
                ]
                items.append(item)
            yield items
            goto.scroll_into_view_if_needed()
            sleep(10)

    def main(self):
        try:
            for items in g.initiate():
                self.all_items += self.all_items + items
        except Exception:
            pass
        finally:
            with open("data.csv", 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Review'])
                for item in self.all_items:
                    writer.writerow(item)
            f.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", '-u', dest='url',help="url of the google map page", required=True)
    parser.add_argument("--limit", '-l', dest='limit', help="reviews limit", default=100, type=int)
    values = parser.parse_args()
    args_dict = vars(values)
    return args_dict['url'],args_dict['limit']

url, limit = parse_args()
if url:
    g = Google(url, limit)
    g.main()
    g.browser.close()
    g.play.stop()
