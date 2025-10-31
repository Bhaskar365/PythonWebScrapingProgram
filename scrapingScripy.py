from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

search_term = input("What products do you want? ")
url = f"https://www.newegg.com/p/pl?d={search_term}&N=4131"

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

driver = webdriver.Chrome(options=options)

# --- Load first page ---
driver.get(url)
time.sleep(8)  # let page load

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

page_text = soup.find(class_="list-tool-pagination-text")

if not page_text or not page_text.strong:
    print("Could not find pagination info — defaulting to 1 page.")
    total_pages = 1
else:
    total_pages = int(page_text.strong.text.rsplit('/')[-1])

print(f"Total pages: {total_pages}")

items_found = {}

# --- Loop through all pages using the SAME browser ---
for page in range(1, total_pages + 1):
    print(f"\n🔹 Scraping page {page}")
    driver.get(f"https://www.newegg.com/p/pl?d={search_term}&N=4131&page={page}")

    time.sleep(6)

    html = driver.page_source
    doc = BeautifulSoup(html, "html.parser")

    div = doc.find(class_="row-body-inner")
    
    # div = doc.find(class_="list items-list-view can-change-list has-quick-view m-gap-t_12 skeleton-loading")

    #print(div)

    if not div:
        print("⚠️ No product container found — possible bot check or no results.")
        continue

    # items = div.find(class_="item-inner")
    items = div.find_all(text=re.compile(search_term))

    #print(items) 
    
    for item in items:
        parent = item.parent

        link = None
        if parent.name != "a":
            continue

        link = parent['href']

        #print(link)

        next_parent = item.find_parent(class_="item-container")
        #print(next_parent)

        price_div = next_parent.find(class_="item-action")

        try:
            price = next_parent.find(class_="price-current").find("strong").string
            items_found[item] = {"price": price,"link":link}
        except:
            pass    

sorted_items = sorted(items_found.items(),key=lambda x:x[1]['price'])
#print(sorted_items)

for item in sorted_items:
    print(item[0])
    print(f"${item[1]['price']}")
    print(item[1]['link'])
    print('----------------------------------')

driver.quit()


