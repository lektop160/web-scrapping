import requests
from bs4 import BeautifulSoup
import fake_useragent
from urllib.parse import *
import time
import sqlite3

# Подключение к базе данных (если файла нет, он будет создан)
conn = sqlite3.connect('kaspi.db')
cursor = conn.cursor()

# Создание таблицы, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        title TEXT,
        date TEXT,
        content TEXT
    )
''')
conn.commit()


def findMainUrl(url, headers):
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
            Scrapping(full_url, headers)
    else:
        print(f"The specified block was not found on the page.      {url}")
        findMainUrl(url, headers)
    
    
def Scrapping(url, headers):
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'lxml')
    block = soup.find('ul', id="questionList")
    if block:
        link_elements = block.find_all('a', href=True)
        print(f"Total 'a href' elements found on {url}: {len(link_elements)}")

        for link_element in link_elements:
            href = link_element.get('href')
            getElements(href, headers, url)
    else:
        print(f"The specified block was not found on the page.      {url}")
     
        
def getElements(url, headers, mainUrl):
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'lxml')
    block = soup.find('ul', id="questionList")
    if block:
        table = block.find('li', class_='kaspiGuide__question--item expanded_block')
        h1 = table.find('h1', class_='kaspiGuide__question--title').text
        date = table.find('span', class_='kaspiGuide__question--description_desktop regular_desc_font').text
        elements = table.find_all('p')
        text = ''
        for element in elements:
            temp = element.text
            text += temp + '\n'
        try:
            cursor.execute('''
            INSERT INTO scraped_data (url, title, date, content)
            VALUES (?, ?, ?, ?)
            ''', (mainUrl, h1, date, text))
            conn.commit()
            print(f"Data inserted successfully for {url}")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    else:
        print(f"The specified block was not found on the page.      {url}")
            

if __name__ == "__main__":
    url = "https://guide.kaspi.kz/client/ru"
    print(f"Process parsing url {url}")
    
    user = fake_useragent.UserAgent().random
    headers = {
        'User-Agent': user,
    }
    
    findMainUrl(url, headers)  

conn.close()