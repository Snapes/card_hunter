import requests
import urllib.request
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import aiohttp
import asyncio
from aiohttp import ClientSession
import re

class Parser(ABC):

    is_json = False

    @abstractmethod
    def get_price(self, response_text, card_name):
        pass

class HareruyaParser(Parser):    
    url = 'https://www.hareruyamtg.com/en/products/search?suggest_type=all&product='
    def __init__(self, language):
        self.name = f'Hareruya {language}'
        self.language = language
        self.key = f"hareyuya{language}"

    def get_price(self, response_text, card_name):
        price_list = []
        soup = BeautifulSoup(response_text, features="html.parser")
        for item in soup.find_all('div', attrs={'class': 'itemData'}):
            try:                
                card = card_name
                language = re.search(fr'【{self.language}】', item.find("a", recursive=True).string, flags=re.IGNORECASE)
                if not language:
                    continue
                name =  re.search(fr'《({card})》', item.find("a", recursive=True).string, flags=re.IGNORECASE).groups(1)[0]
                stock = int(re.search(r"【NM Stock:(\d)】", item.find("p", attrs={'class': 'itemDetail__stock'}, recursive=True).string).groups(1)[0])
                price = int(re.search(r"¥ ([\d,]*)", item.find("p", attrs={'class': 'itemDetail__price'}, recursive=True).string).groups(1)[0].replace(',',''))
                if stock <= 0:
                    continue 
                price_list.append(round(price/77, 2))
            except AttributeError:
                continue
        return min(price_list) if len(price_list) > 0 else -1


class HobbymasterParser(Parser):
    name = 'Hobbymaster'
    url = 'https://hobbymaster.co.nz/cards/get-cards?foil=0&lang=&game=1&_search=true&sidx=set&sord=desc&name='
    key = 'hobbymaster'

    def get_price(self, response_text, card_name):
        data = json.loads(response_text)
        price_list = []
        if 'rows' in data:
            for item in data['rows']:
                if card_name.lower() in item['cell'][0].lower():
                    if item['cell'][12] == 0:
                        continue
                    else:
                        price = item['cell'][10]
                        price = float(price.replace('$', '').replace('!', ''))
                        price_list.append(price)
            if len(price_list) == 0:
                price = -1
            else:
                price = min(price_list)
        else:
            price = -1
        return price

class BaydragonParser(Parser):
    name = 'Baydragon'
    url = 'https://www.baydragon.co.nz/search/category/01?searchType=single&searchString='
    key = 'baydragon'

    def get_price(self, response_text, card_name):
        soup = BeautifulSoup(response_text, features="html.parser")
        div = soup.find('div', attrs={'class': 'tcgSingles'})
        table = div.find('table')
        tds = table.find_all('td')
        n = 0
        price_list = []
        for td in tds:
            n += 1
            if n > len(tds):
                break
            if 'NZ$' in td.text:
                if card_name in tds[n-6].text:
                    if int(tds[n].text) > 0:
                        price = float(td.text.replace('NZ$', ''))
                        price_list.append(price)
        if len(price_list) == 0:
            price = -1
        else:
            price = min(price_list)
        return price

class GoblinGamesParser(Parser):
    name = 'Goblin Games'
    url = 'https://goblingames.nz/search?q='
    key = "goblingames"

    def get_price(self, response_text, card_name):
        soup = BeautifulSoup(response_text, features="html.parser")
        products = soup.find_all('div', attrs={'class': 'productCard__lower'})
        price_list = []
        for product in products:
            p_list = product.find_all('ul')
            for item in p_list:
                instock = item.find_all('li')
                if len(instock):
                    for i in instock:
                        title = i.attrs['data-producttitle']
                        price = int(i.attrs['data-price']) / 100
                    if card_name.lower() in title.lower():
                        price_list.append(price)
        if len(price_list) == 0:
            price = -1
        else:
            price = min(price_list)
        return price

class ShopifyParser(Parser):
    def __init__(self, url, name, key):
        self.url = url
        self.name = name
        self.key = key

    def get_price(self, response_text, card_name):
    #     soup = BeautifulSoup(html_content, "lxml")
        soup = BeautifulSoup(response_text, features="html.parser")
        products = soup.find_all('div', attrs={'class': 'product Norm'})
        price_list = []
        for product in products:
            title = product.find('p', attrs='productTitle').text.replace('\n', ' ').strip()
            price = product.find('p', attrs='productPrice').text.replace('\n', ' ').strip()
            if card_name.lower() in title.lower():
                if price == 'Varies':
                    prices = product.parent.find('div', attrs={'class': 'buyWrapper'}).find_all('p')
                    for p in prices:
                        try:
                            price = float(p.text.split('$')[1])
                        except:
                            continue
                        price_list.append(price)
                elif '$' in price:
                    try:
                        price = float(price.replace('$', ''))
                    except:
                        continue
                    price_list.append(price)
                else:
                    if price != 'Sold Out':
                        price_list.append(price)
        if len(price_list) == 0:
            price = -1
        else:
            price = min(price_list)

        return price



class CardSearcher():
    parsers = [
        HobbymasterParser(),
        HareruyaParser(language="EN"),
        HareruyaParser(language="JP"),
        BaydragonParser(),
        GoblinGamesParser(),
        ShopifyParser('https://spellboundgames.co.nz/search?q=', 'Spellbound', 'spellbound'),
        ShopifyParser('https://magicatwillis.co.nz/search?q=', 'Magic at Willis', 'willis'),
        ShopifyParser('https://ironknightgaming.co.nz/search?q=', 'Iron Knight Gaming', 'ironknight'),
        ShopifyParser('https://mtgmagpie.com/search?q=', 'Magic Magpie', 'magpie')
    ]
    price_data = []

    # async def run_search(self, cards):
    #     self.find_card(cards)
    #     return self.display_prices()
    async def parse_price(self, session, parser, card):
        resp = await session.get(parser.url + card)
        response = await resp.text()
        return parser.get_price(response, card)

    def get_prices(self, card):
        asyncio.run(self.await_get_prices(card))

    async def await_get_prices(self, card):
        self.price_data = [card]
        async with aiohttp.ClientSession() as session:
            tasks = []
            for parser in self.parsers:
                tasks.append(self.parse_price(session, parser, card))                   
            prices = await asyncio.gather(*tasks, return_exceptions=True)
        self.price_data += prices
                    
    def search_card(self, card):
        self.get_prices(card)
        return self.price_data

    def get_headers(self):
        return ["Card"] + list(parser.name for parser in self.parsers)