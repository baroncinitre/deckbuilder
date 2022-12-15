import sf_price_fetcher
from deckBuilder import deckBuilder
from mtgtools.MtgDB import MtgDB
from mtgtools.PCardList import PCardList
from mtgtools.PSetList import PersistentList

# TODO: currently only configured for EDH, check if functions work with duplicate cards

def main():
    # Current db is 'test_db.fs'
    builder = deckBuilder('test_db.fs', 'testdeck')
    builder.print_planned_swaps()

if __name__ == "__main__":
    main()