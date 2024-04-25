

import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from scrapy import Selector
from pandas import json_normalize

import rottentomatoes as rt
from json import (
  JSONEncoder,
  dumps as json_dumps,
  loads as json_loads,
)



class Scraper:

    def __init__(self, domain: str):
        self.base_url = domain
        self.headers = {
            "referer": domain,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self.builder = "lxml"

    def get_parsed_page(self, path: str) -> BeautifulSoup:
        
        url = self.base_url + path
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  
        except requests.RequestException as e:
            raise Exception(f"Error connecting to {url}: {e}")

        try:
            dom = BeautifulSoup(response.text, self.builder)
        except Exception as e:
            raise Exception(f"Error parsing response from {url}: {e}")

        if response.status_code != 200:
            message = dom.find("section", {"class": "message"})
            message = message.strong.text if message else None
            messages = json.dumps({
                'code': response.status_code,
                'reason': str(response.reason),
                'url': url,
                'message': message
            }, indent=2)
            raise Exception(messages)
        return dom
            
    def get_link(self) -> str:
        url = self.base_url
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  
        except requests.RequestException as e:
            raise Exception(f"Error connecting to {url}: {e}")
    
        try:
            dom = BeautifulSoup(response.text, self.builder)
            cont = dom.select_one("head > meta[property='og:url']")
            if cont:
                link = cont['content']
            else:
                raise Exception("Meta tag 'og:url' not found.")
        except Exception as e:
            raise Exception(f"Error parsing response from {url}: {e}")
        return link
    
    def extract_reviews(self, soup: BeautifulSoup, num_reviews: int = 12) -> list:
        reviews = []
        film_details = soup.find_all('li', class_='film-detail')
        for film_detail in film_details:
            spoilers_div = film_detail.find('div', 
                                            class_='hidden-spoilers expanded-text')
            if spoilers_div:
                review_text = spoilers_div.text.strip()
            else:
                review_text = film_detail.find('div', 
                                               class_='body-text -prose collapsible-text'
                                              ).text.strip()
            reviews.append(review_text)
            if len(reviews) == num_reviews: 
                break
        return reviews
    
    @staticmethod
    def get_reviews_from_link(domain: str, num_reviews: int = 12) -> list:
        
        scraper = Scraper(domain)
        link = scraper.get_link()
        scraper = Scraper(link)
        path = 'reviews/by/activity/'
        dom = scraper.get_parsed_page(path)
        
        return scraper.extract_reviews(dom, num_reviews)

