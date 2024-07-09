import os
from webSearch import search
from webScraping import scrapper_main

def main():
    try:
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
                if os.path.exists("kaspi.db"):
                    os.remove("kaspi.db")
                    print("Existing kaspi.db removed.")
                scrapper_main()
            elif choose.upper() == "N":
                exit()
            else:
                print("Invalid input. Exiting.")
                exit()
        elif num == 2:
            search()
        else:
            print("Invalid input. Please choose 1 or 2.")
    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()
