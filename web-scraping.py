import requests
from bs4 import BeautifulSoup
import fake_useragent
from urllib.parse import *
import time
import sqlite3

# Connect to the SQLite database. If the database does not exist, it will be created.
conn = sqlite3.connect('kaspi.db')
cursor = conn.cursor()

# Create a table named 'scraped_data' if it does not exist.
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
    """
    This function sends a GET request to the specified URL and extracts all 'a href' elements from a specific block.
    It then processes each extracted URL by calling the 'Scrapping' function.

    Parameters:
    url (str): The URL to send the GET request to.
    headers (dict): The headers to include in the GET request.

    Returns:
    None
    """
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
    """
    This function sends a GET request to the specified URL and extracts all 'a href' elements from a specific block.
    It then processes each extracted URL by calling the 'getElements' function.

    Parameters:
    url (str): The URL to send the GET request to.
    headers (dict): The headers to include in the GET request.

    Returns:
    None
    """
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
    """
    This function sends a GET request to the specified URL and extracts specific elements from a specific block.
    It then inserts the extracted data into the 'scraped_data' table in the SQLite database.

    Parameters:
    url (str): The URL to send the GET request to.
    headers (dict): The headers to include in the GET request.
    mainUrl (str): The original URL from which the current URL was extracted.

    Returns:
    None
    """
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
