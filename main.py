import sf_price_fetcher
from deckBuilder import deckBuilder
from mtgtools.MtgDB import MtgDB
from mtgtools.PCardList import PCardList
from mtgtools.PSetList import PersistentList

#TODO: repeat card checks for addition (ignore basic lands) and all swaps
#TODO: currently only focusing on EDH, check if functions work with duplicate cards (maybe. non-EDH is lame)
#TODO: implement swap execute
#TODO: indexed removal with cards displayed sorted by type (land, creature, etc)
#TODO: active UI in console (have enterable commands like remove to trigger removal, etc)
#TODO: removal console UI
#TODO: better addition functionality through console
#TODO: exporting (export directly to apps via API?)

# Pipe dreams: Flask app, GUI

def main():
    # Current db is 'test_db.fs'
    builder = deckBuilder('test_db.fs', 'mmcurrent')
    builder.print_planned_swaps()

if __name__ == "__main__":
    main()