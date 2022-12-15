import sf_price_fetcher
from mtgtools.MtgDB import MtgDB
from mtgtools.PCardList import PCardList
from mtgtools.PSetList import PSetList

class deckBuilder:
    def __init__(self, db_name, deck_var_name):
        self.deck_var_name = deck_var_name
        self.db = MtgDB(db_name)
        self.cards = self.db.root.scryfall_cards
        self.sets = self.db.root.scryfall_sets
        self.deck = getattr(self.db.root, deck_var_name)
        
    @staticmethod
    def create_deck(db, deck_name, deck_var_name):
        deck = PCardList()
        deck.name = deck_name
        setattr(db.root, deck_var_name, deck)
        db.commit()

    def print_decklist(self):
        print(self.deck.deck_str())

    def save(self):
        self.db.commit()

    def remove_at_index(self, index, commit=True):
        self.deck.pop(index)
        self.save()

    def remove_card(self, card_name, commit=True, strict=True, deck=None):
        # Takes the first result of the search. Name must match exactly if strict is True
        if deck != None:
            to_modify = deck
        else:
            to_modify = self.deck

        search_func_dispatch = {True: self.deck.where_exactly, False: self.deck.where}
        try:
            to_remove = search_func_dispatch[strict](name=card_name)[0]
            to_modify.remove(to_remove)
            if commit: self.save()
            return 0
        except IndexError:
            print("No match in deck - check the name is spelled correctly (case insensitive)")
            return 1

    def add_card(self, card_name, commit=True, strict=True, deck=None):
        # Takes the first result of the search. Name must match exactly if strict is True
        if deck != None:
            to_modify = deck
        else:
            to_modify = self.deck

        search_func_dispatch = {True: self.cards.where_exactly, False: self.cards.where}
        to_add = search_func_dispatch[strict](name=card_name)[0]
        try:
            to_modify.append(to_add)
            if commit: self.save()
            return 0
        except IndexError:
            print("No match - check the name is spelled correctly (case insensitive)")
            return 1

    def swap(self, card_out, card_in, out_strict=True, in_strict=True, out_commit=True, in_commit=True):
        self.remove_card(card_out, strict=out_strict, commit=out_commit)
        self.add_card(card_in, strict=in_strict, commit=in_commit)

    def plan_swap(self, card_out, card_in, commit=True):
        out_list_name = f"{self.deck_var_name}_swap_out"
        in_list_name = f"{self.deck_var_name}_swap_in"
        try:
            out_list = getattr(self.db.root, out_list_name)
            in_list = getattr(self.db.root, in_list_name)
        except:
            self.create_deck(self.db, out_list_name, out_list_name)
            self.create_deck(self.db, in_list_name, in_list_name)
            out_list = getattr(self.db.root, out_list_name)
            in_list = getattr(self.db.root, in_list_name)
        if self.add_card(card_out, deck=out_list):
            print("Error setting out card, please try again")
            return
        if self.add_card(card_in, deck=in_list):
            print("Error setting in card, please try again")
            self.remove_card(card_out, deck=out_list)
            return

    def execute_swaps(self):
        pass

    def print_planned_swaps(self):
        out_list_name = f"{self.deck_var_name}_swap_out"
        in_list_name = f"{self.deck_var_name}_swap_in"
        try:
            out_plist = getattr(self.db.root, out_list_name)
            in_plist = getattr(self.db.root, in_list_name)
        except:
            print("No swaps planned")
            return
        
        out_cards = out_plist.cards
        in_cards = in_plist.cards
        for i in range(len(out_cards)):
            print(out_cards[i].name + '\t ' + in_cards[i].name)