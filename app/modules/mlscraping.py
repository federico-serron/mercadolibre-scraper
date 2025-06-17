import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

# Función para obtener un user agent aleatorio o uno fijo si fake_useragent falla
def get_random_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        # Fallback a un user agent común de Chrome
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

from multiprocessing import Pool
from slugify import slugify

# Getting all the links from the results
def get_list(url, search_term):
    product_links = []
    headers = {'User-Agent': get_random_user_agent()}
    search_term_slug = slugify(search_term)
    
    k = requests.get(f'{url}/{search_term_slug}', headers=headers, timeout=7)
    if k.status_code != 200:
        quit()

    k = k.text
    soup = BeautifulSoup(k, 'html.parser')

    # Getting the total number of pages
    try:
        total_page_count = soup.find_all('li', class_='andes-pagination')
        page_count = total_page_count[-1]
        #page_count = int(page_count.split(' ')[-1])
        print(page_count)
    except:
        page_count=1

    # Navigation through the pagination
    for x in range(1, page_count + 1):
        if x == 1 and page_count > 1:
            next_page = soup.find('a', {'class': 'andes-pagination__link shops__pagination-link ui-search-link'}).get('href')
            if next_page is not None:
                next_page = next_page.split('/')
                last_term = next_page[-1].split('_', 1)
                next_page[-1:] = last_term[0], last_term[1] # 0 is the search term
                next_page[-1] = next_page[-2] + '_' + next_page[-1] # -2 is the search term
                next_page = '/'.join(next_page)  
            
        elif x < page_count and page_count > 1:
            k = requests.get(next_page, headers=headers, timeout=7)
            if k is not None:
                k = k.text
            soup = BeautifulSoup(k, 'html.parser')
            next_page = soup.find('a', {'class': 'andes-pagination__link shops__pagination-link ui-search-link'}).get('href')
            if next_page is not None:
                next_page = next_page.split('/')
                last_term = next_page[-1].split('_', 1)
                next_page[-1:] = last_term[0], last_term[1] # 0 is the search term
                next_page[-1] = next_page[-2] + '_' + next_page[-1] # -2 is the search term
                next_page = '/'.join(next_page)
            
        elif x == page_count and page_count >= x+1:
            k = requests.get(next_page, headers=headers, timeout=7)
            if k is not None:
                k = k.text
            soup = BeautifulSoup(k, 'html.parser')
            
        
        # Catching all the products's links and save them into a list
        products_list = soup.find_all('li', {'class': 'ui-search-layout__item shops__layout-item'})
        if products_list is not None:
            for product in products_list:
                link = product.find('a', {'class': 'ui-search-link'}).get('href')
                if link is not None:
                    if 'click1' not in link:
                        product_links.append(link)
                    else:
                        continue
        else:
            print('List of elements not found!')
            quit()
            
    return product_links


# Function to access to each link 
def parse(link):
    
    headers = {'User-Agent': get_random_user_agent()}
    
    f = requests.get(link, headers=headers, timeout=7)
        
    if f.status_code != 200:
        print('Could not access to link')
        quit()
            
    f = f.text
    hun = BeautifulSoup(f, 'html.parser')
        
    try:
        price_symbol = hun.find('span', {'class': 'andes-money-amount__currency-symbol'}).text.replace('\n', '').strip()
        price = hun.find('span', {'class': 'andes-money-amount__fraction'}).text.replace('\n',"").strip()
                 
    except:
        price = None
                
    try:
        image = hun.find('img', {'class': 'ui-pdp-image ui-pdp-gallery__figure__image'})['data-zoom']
    except:
        image = None
                    
    try:
        sells_qty = hun.find('span', {'class': 'ui-pdp-subtitle'}).text.replace('\n',"").strip()
        sells_qty = sells_qty.split(' ')
        sells_qty = sells_qty[-2]
    except:
        sells_qty = None
                    
    try:
        title = hun.find('h1', {'class': 'ui-pdp-title'}).text.replace('\n',"").strip()
    except:
        title = None
            
    try:
        rating_link = hun.find('a', {'class': 'ui-pdp-review__label ui-pdp-review__label--link'}).get('href')
        r = requests.get(rating_link)
        rating_soup = BeautifulSoup(r, 'html.parser')
        rating = rating_soup.find('p', {'class': 'ui-review-capability__rating__average ui-review-capability__rating__average--desktop'}).text
    except:
        rating = None
            
    item_data = {
        'title': title,
        'image': image,
        'sells': sells_qty,
        'price': price,
        'rating': rating,
        'link': link
    }
        
    return item_data


def makeScrap(links):
    with Pool(1) as p:
        records = p.map(parse, links)
    
    return records



###############################################################
url = 'https://listado.mercadolibre.com.uy'

if __name__ == '__main__':
    search_term = input('Please, type what you are looking for: ')
    
    products = get_list(url, search_term)
    records = makeScrap(products)
        
    # Printing dataframe
    df = pd.DataFrame(records)
    print(df)