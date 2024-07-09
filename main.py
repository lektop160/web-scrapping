from webSearch import search
from webScraping import Scrapper

if __name__ == "__main__":
    print("""• Choose operation: 
    1] Scraping Kaspi
    2] Search information""")
    num = int(input("Choose a number: "))
    if num == 1:
        print("In process removed base data and run scraping website.")
        print("Do you give access?")
        print("Y/N")
        choose = input("")
        if choose.upper() == "Y":
            Scrapper().run()
        elif choose.upper() == "N":
            exit()
        else:
            exit()
    else:
        search()
    
