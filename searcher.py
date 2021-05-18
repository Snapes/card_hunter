from CardSearcher import CardSearcher
import pandas as pd


card_searcher = CardSearcher()
cards = ["Feast on the Fallen", "Unspeakable Symbol"]
prices = []
for card in cards:
    # print(f"Getting prices for {card}")
    prices.append(card_searcher.search_card(card))
    print(card_searcher.search_card(card))
columns = ["Card"] + list(parser.name for parser in card_searcher.parsers)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
print(pd.DataFrame(prices, columns=columns))


#                         Card  Hobbymaster  Hareruya EN  Hareruya JP  Baydragon  Goblin Games  Spellbound  Magic at Willis  Iron Knight Gaming  Magic Magpie
# 0          Archmage Emeritus         -1.0        10.39         1.30       3.60           2.5         3.0             -1.0                  -1            -1
# 1   Deekah, Fractal Theorist         -1.0        -1.00         3.90       1.66           1.5         2.1             -1.0                  -1            -1
# 2         Chandra's Ignition         -1.0        -1.00         6.49      -1.00          -1.0        -1.0              8.5                  -1            -1
# 3   Veyran, Voice of Duality         -1.0        -1.00        -1.00      21.36          22.0        -1.0             -1.0                  -1            -1
# 4  Zaffir, Thunder Conductor         -1.0        -1.00        -1.00      -1.00          -1.0        -1.0             -1.0                  -1            -1
# 5  Jadzi, Oracle of Arcavios          4.8         6.49        32.47      -1.00           5.0        -1.0             -1.0                  -1            -1
# 6     Octavia, Living Thesis          1.8        -1.00        -1.00       5.22           3.5        -1.0             -1.0                  -1            -1
# 0       Spawnbroker          0.9          3.9         3.90         -1           0.7         1.5              0.7                  -1         -1.00
# 1  Puppeteer Clique         -1.0          2.6         0.65         -1           7.5        -1.0              7.6                  -1          9.55