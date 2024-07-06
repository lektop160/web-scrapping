import sqlite3
import keyboard as keyb
from fuzzywuzzy import fuzz

def search():
    def search_database(query):
        # Подключение к базе данных
        conn = sqlite3.connect('kaspi.db')
        cursor = conn.cursor()
        
        # Разделение введенного текста на слова
        query_words = query.split()

        # Инициализация списка для хранения найденных результатов
        results = []

        # SQL-запрос для поиска точного совпадения по заголовку и содержимому
        for word in query_words:
            cursor.execute('''
                SELECT url, title, date, content, content_url
                FROM scraped_data 
                WHERE title LIKE ?
                OR content LIKE ?
            ''', ('%' + word + '%', '%' + word + '%'))
            
            # Извлечение всех найденных строк и добавление в список результатов
            results += cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()
        
        return results

    query = input("Введите текст для поиска: ")
    
    results = search_database(query)
    
    if results:
        print(f"Найдено {len(results)} записей:")
        for result in results:
            print("URL:", result[0])
            print("Title:", result[1])
            print("Date:", result[2])
            print("Content:", result[3],'\n')
            print("Content url:", result[4])
            print("="*50)
            
        print("Press [Enter]...")
        keyb.wait('Enter')
            
    else:
        print("Ничего не найдено по вашему запросу.")
