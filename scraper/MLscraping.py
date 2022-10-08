import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
from multiprocessing import Pool


# Getting all the links from the results
def get_list(url, search_term):
    product_links = []
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    
    k = requests.get(f'{url}/{search_term}', headers=headers, timeout=7)
    if k.status_code != 200:
        quit()

    k = k.text
    soup = BeautifulSoup(k, 'html.parser')

    # Obtengo el numero de paginas y lo convierto a un int
    try:
        page_count = soup.find('li', {'class': 'andes-pagination__page-count'}).text
        page_count = int(page_count.split(' ')[-1])
    except:
        page_count=1

    for x in range(1, page_count + 1):
        # Aca tengo que cambiar lo que va despues de la barra, eso es lo que debe ingresar el cliente, asi que debe ser DINAMICO
        if x == 1 and page_count > 1:
            next_page = soup.find('a', {'class': 'andes-pagination__link shops__pagination-link ui-search-link'}).get('href')
            if next_page is not None:
                next_page = next_page.split('/')
                last_term = next_page[-1].split('_', 1)
                next_page[-1:] = last_term[0], last_term[1] #El 0 es el termino de busqueda
                next_page[-1] = next_page[-2] + '_' + next_page[-1] # El -2 es el termino de busqueda
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
                next_page[-1:] = last_term[0], last_term[1] #El 0 es el termino de busqueda
                next_page[-1] = next_page[-2] + '_' + next_page[-1] # El -2 es el termino de busqueda
                next_page = '/'.join(next_page)
            
        elif x == page_count and page_count >= x+1:
            k = requests.get(next_page, headers=headers, timeout=7)
            if k is not None:
                k = k.text
            soup = BeautifulSoup(k, 'html.parser')
            
        
        # Busco todos los links de los productos en el listado de resultados
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
def parse(product_links):
    
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    data = []
    
    for link in product_links:
        f = requests.get(link, headers=headers, timeout=7)
        
        if f.status_code != 200:
            print('Could not access to link')
            quit()
            
        f = f.text
        hun = BeautifulSoup(f, 'html.parser')
        
        try:
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
            rating = hun.find('span', {'class': 'ui-pdp-review__amount'}).text.replace('\n',"").strip()
        except:
            rating = None
            
        item_data = {
            'title': title,
            'image': image,
            'Sells': sells_qty,
            'price': price
        }
        data.append(item_data)
        
    return data


search_term = 'huevo-diarrea'
url = 'https://listado.mercadolibre.com.ar'

products = get_list(url, search_term)

if __name__ == '__main__':
    p = Pool(5)  # Pool tells how many at a time
    records = p.map(parse, products)
    p.terminate()
    p.join()