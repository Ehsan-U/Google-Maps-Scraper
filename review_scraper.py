
""" Selenium based scraper for scraping reviews from Google maps """

import csv
import json
import os
import time
import urllib.parse
from scrapy.selector import Selector
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class Review_Crawler():

    def __init__(self,):
        self.url = "https://www.google.com/search?q="
        self.system_name = os.getlogin()
        # self.profile = r'C:\Users\{system_name}\AppData\Local\Google\Chrome\User%20Data\Default'
        self.opt = ChromeOptions()
        self.opt.add_argument(rf'user-data-dir=C:\Users\{self.system_name}\AppData\Local\Google\Chrome\User%20Data\Default')
        self.driver = uc.Chrome(options=self.opt,use_subprocess=True)
        self.action = ActionChains(driver=self.driver)

    # go to each place and scrape reviews and save into file
    def scrape_reviews(self,url, driver, filename):
        file = open(f"{filename}.csv", 'w', newline='', encoding='utf-8')
        writer = csv.writer(file)
        writer.writerow(['Date','Name','Review'])
        driver.get(url)
        try:
            self.driver.find_element(by=By.XPATH,value="//a[contains(@data-async-trigger,'review')][1]").click()
        except:
            raise " [+] No reviews found! skipping.."
        else:
            i = 1
            while True:
                time.sleep(3)
                sel = Selector(text=self.driver.page_source)
                reviews = sel.xpath("//div[contains(@class,'reviews-block')]/div")
                print('\r', len(reviews), end='')
                if len(reviews) >= self.reviews_count:
                    break
                else: # //div[contains(@class,'reviews-block')]/div//span[@class='review-snippet']
                    last = self.driver.find_element(by=By.XPATH,value="(//div[contains(@class,'reviews-block')]/div)[last()]").location_once_scrolled_into_view
                    continue
            for review in reviews:
                try:
                    name = review.xpath(".//div[@style='display:block'][1]//a/text()").get()
                    timestamp = review.xpath(".//div[@style='vertical-align:top'][1]//g-review-stars/following-sibling::span[1]/text()").get()
                    raw_review = "".join(review.xpath(".//span[@tabindex='-1']//text()").getall())
                except:
                    i+=1
                else:
                    writer.writerow([timestamp, name, raw_review])
                    if i == self.reviews_count:
                        print(f"\n [+] Reviews Scraped: {i}")
                        break
                    else:
                        i+=1
                        continue
        file.close()

    # load the settings
    def load_config(self):
        with open("config.json") as f:
            config = json.load(f)
        places = config['places']
        self.reviews_count = config['reviews_count']
        for data in self.build_urls(places):
            url = data[0]
            filename = data[-1]
            self.scrape_reviews(url, self.driver, filename)
        self.driver.close()

    # build urls from places
    def build_urls(self,places):
        for place in places:
            encoded = urllib.parse.quote_plus(place)
            url = self.url + encoded
            filename = place.strip().replace(' ','')
            yield [url,filename]

if __name__ == "__main__":
    review_scraper = Review_Crawler()
    review_scraper.load_config()
