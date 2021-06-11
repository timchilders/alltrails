import time
import pprint
import pandas as pd
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
    

def get_driver(url, class_name, headless=True, retries=0):
    
    try:
        options = Options()
        ua = UserAgent()
        userAgent = ua.random
        print(userAgent)
        options.add_argument(f'user-agent={userAgent}')
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--incognito")
        options.add_argument("--enable-javascript")
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
#         options.add_argument("user-data-dir=selenium")
        
        driver = webdriver.Chrome("/home/tim/DSI/capstones/alltrails/chromedriver",options=options)
        driver.get(url)
        WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,class_name)))
    except (TimeoutException,WebDriverException):
        retries+=1
        print(f'Retry #: {retries}')
        if retries<5:
            driver.close()
            return get_driver(url,class_name,headless=False,retries=retries)
        else:
            driver.quit()
    else:
        page = driver.page_source
        driver.close()
        return page

def create_db(soup):
    #driver function for creating dataframe from trail pages
    urls=[]
    cards = soup.findAll('div', attrs = {'class':'styles-module__containerDescriptive___3aZqQ styles-module__trailCard___2oHiP'})
    for trail in cards:
        urls.append('https://www.alltrails.com/'+trail.attrs['itemid'])

    df = get_trail_info(urls)
    return df

def page_parser(page,url):
    #Pages html for information. Returns information as pandas series.
    #header
    header = page.find('div',id='title-and-menu-box')
    trail_name = header.find('h1').text
    difficulty = header.find('span').text
    reviews = header.find('meta', attrs = {'itemprop':'reviewCount'})['content']
    loc = header.find('a', attrs = {'class':'xlate-none styles-module__location___11FHK styles-module__location___3wEnO'})['title']
    photos = header.find('span',attrs = {'class':'styles-module__title___skfpX'}).text
    
    #trail stats section
    trail_stats = page.findAll('span', attrs={'class':'styles-module__detailData___kQ-eK'})
    length = trail_stats[0].text
    elev_gain = trail_stats[1].text
    route = trail_stats[2].text
    
    #metadata
    lat = page.find('meta', attrs = {'itemprop':'latitude'})['content']
    long = page.find('meta', attrs = {'itemprop':'longitude'})['content']
    
    #tags
    tags = page.find_all('span', attrs = {'class':'big rounded active'})
    tags = [tag.text for tag in tags]
    
    description = page.find('p',id='text-container-description').text
#     rating = page.find('div', attrs={'class':'styles-module__ratingDisplay___1vR1p'}).text
    rating=0
    
    row = pd.Series([trail_name,loc,rating,reviews,difficulty,length,elev_gain,route,photos,lat,long,tags,description,url], 
                    index=['Name','Location','Rating','Reviews','Difficulty','Length','Elevation gain','Route type','Photos','lat','long','tags','description','URL'])
    return row


def get_trail_info(urls):
    class_name='styles-module__content___1GUwP'
    df = pd.DataFrame(columns=['Name','Location','Rating','Reviews','Difficulty','Length','Elevation gain','Route type','Photos','lat','long','tags','description','URL'])
    for url in urls:
        try:
            page = get_driver(url,class_name, headless=False)
            time.sleep(5)
            row = page_parser(BeautifulSoup(page,'html.parser'),url)
            df = df.append(row, ignore_index=True)
            name = df['Name']
            print(f'scraped: {name}')
        except:
            print(f'Error scraping {url}')
            break
    return df
            

def get_trails(driver):
    url = 'https://www.alltrails.com/us/colorado'
    driver.get(url)
    wait = WebDriverWait(driver,20)

    while True:
        try:
            show_more = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.styles-module__button___1nuva')))
            show_more.click()
            time.sleep(1)
        except:
            break
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup


def go_login(un, pw):
    #function to login to alltrails in order to get all information from each page
    #does not return
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver=webdriver.Chrome("/home/tim/DSI/capstones/alltrails/chromedriver", options=options)
    url = 'https://www.alltrails.com/login?ref=header'
    driver.get(url)
    time.sleep(5)
    
    username = driver.find_element_by_name('userEmail')
    username.send_keys(un)
    password = driver.find_element_by_name('userPassword')
    password.send_keys(pw)

    login = driver.find_element_by_css_selector(".styles-module__submit___2REmT")
    login.click()
    time.sleep(5)



if __name__ == "__main__":
    #login if needed
    url = 'https://www.alltrails.com/login?ref=header'
    un = 'username'
    pwd = 'password'
    go_login(un,pwd)

    #get trail cards from colorado page
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver=webdriver.Chrome("/home/tim/DSI/capstones/alltrails/chromedriver", options=options)
    soup = get_trails(driver)
    driver.quit()

    #initiate scraping of each trail url
    db = create_db(soup)