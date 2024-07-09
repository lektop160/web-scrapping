import requests
from bs4 import BeautifulSoup
import fake_useragent
from urllib.parse import urljoin
import time
import sqlite3

class Scrapper:
    def __init__(self):
        self.conn = sqlite3.connect('kaspi.db')
        self.cursor = self.conn.cursor()

        # Create a table named 'scraped_data' if it does not exist.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                date TEXT,
                content TEXT,
                content_url TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def find_main_url(self, url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        block = soup.find('ul', class_="main-left-menu kaspiGuide__product--list")
        if block:
            link_elements = block.find_all('a', href=True)
            print(f"Total 'a href' elements found: {len(link_elements)}")
            time.sleep(1)

            for link_element in link_elements:
                href = link_element.get('href')
                full_url = urljoin(url, href)
                print(f"Process new URL: {full_url}")
                self.scrapping(full_url, headers)
        else:
            print(f"The specified block was not found on the page. {url}")

    def scrapping(self, url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        block = soup.find('ul', id="questionList")
        if block:
            link_elements = block.find_all('a', href=True)
            print(f"Total 'a href' elements found on {url}: {len(link_elements)}")

            for link_element in link_elements:
                href = link_element.get('href')
                self.get_elements(urljoin(url, href), headers, url)
        else:
            print(f"The specified block was not found on the page. {url}")

    def get_elements(self, url, headers, main_url):
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        block = soup.find('ul', id="questionList")
        if block:
            table = block.find('li', class_='kaspiGuide__question--item expanded_block')
            if table:
                h1 = table.find('h1', class_='kaspiGuide__question--title').text
                date = table.find('span', class_='kaspiGuide__question--description_desktop regular_desc_font').text
                elements = table.find_all('p')
                text = '\n'.join([element.text for element in elements])
                
                try:
                    self.cursor.execute('''
                        INSERT INTO scraped_data (url, title, date, content, content_url)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (main_url, h1, date, text, url))
                    self.conn.commit()
                    print(f"Data inserted successfully for {url}")
                except sqlite3.Error as e:
                    print(f"Error inserting data: {e}")
            else:
                print(f"No table found in the block. {url}")
        else:
            print(f"The specified block was not found on the page. {url}")

    def run(self):
        url = "https://guide.kaspi.kz/client/ru"
        print(f"Process parsing url {url}")
        
        user = fake_useragent.UserAgent().random
        headers = {
            'User-Agent': user,
        }
        
        self.find_main_url(url, headers)
        self.conn.close()

def scrapper_main():
    scrapper = Scrapper()
    scrapper.run()
