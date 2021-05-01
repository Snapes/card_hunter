from CardSearcher import CardSearcher
import pandas as pd


card_searcher = CardSearcher()
cards = ["Cauldron of Souls","Unspeakable Symbol", "Trophy Mage"]
prices = []
for card in cards:
    print(f"Getting prices for {card}")
    prices.append(card_searcher.search_card(card))
columns = ["Card"] + list(parser.name for parser in card_searcher.parsers)
print(pd.DataFrame(prices, columns=columns))