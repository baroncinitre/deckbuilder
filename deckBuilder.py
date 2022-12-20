import sf_price_fetcher
import copy
import os
from pprint import pprint
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
    
    @staticmethod
    def duplicate_deck(db, old_deck_var_name, new_deck_var_name, new_deck_name=''):
        new_deck = copy.deepcopy(getattr(db.root, old_deck_var_name))
        if new_deck_name: 
            new_deck.name = new_deck_name
        else:
            new_deck.name = new_deck_var_name
        setattr(db.root, new_deck_var_name, new_deck)
        db.commit()

    @staticmethod
    def print_stored_pcardlists(db):
        db_vars = db.root._root.data.keys()
        pprint(db_vars)

    def print_decklist(self):
        print(self.deck.deck_str())
    
    def print_ordered_decklist(self):
        for (i, item) in enumerate(self.deck.cards, start=0):
            print(f"{i}: {item}")

    def save(self):
        self.db.commit()

    def remove_at_index(self, index, commit=True, deck=None):
        if deck != None:
            to_modify = deck
        else:
            to_modify = self.deck

        if type(index) == list:
            # This sorts and flips, removing from highest index to lowest
            # this SHOULD always mean indices stay the same. TODO: verify
            indices = sorted(index, reverse=True)
            for i in indices:
                to_modify.pop(i)
        else:
            to_modify.pop(index)

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

    # WARNING: finnicky for some reason
    def add_from_file(self, fp, strict=False):
        f = open(fp, "r")
        data = f.read()
        cards_to_add = data.split("\n")
        failed_additions = []
        for card in cards_to_add:
            result = self.add_card(card, strict=strict)
            if result: failed_additions.append(card)
        print("\nFailed cards:")
        print(failed_additions)


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

    def plan_swap(self, card_out, card_in, strict=True):
        #TODO make this less ugly
        out_list_name = f"{self.deck_var_name}_swap_out"
        in_list_name = f"{self.deck_var_name}_swap_in"

        try:
            out_list = getattr(self.db.root, out_list_name)
            in_list = getattr(self.db.root, in_list_name)
        except:
            self.create_deck(self.db, out_list_name, out_list_name)
            self.create_deck(self.db, in_list_name, in_list_name)
            # gross
            out_list = getattr(self.db.root, out_list_name)
            in_list = getattr(self.db.root, in_list_name)

        if self.add_card(card_out, deck=out_list, strict=strict):
            print("Error setting out card, please try again")
            return
        if self.add_card(card_in, deck=in_list, strict=strict):
            print("Error setting in card, please try again")
            self.remove_card(card_out, deck=out_list)
            return

    def remove_swap(self, card_out, card_in, strict=True):
        out_list_name = f"{self.deck_var_name}_swap_out"
        in_list_name = f"{self.deck_var_name}_swap_in"

        try:
            out_list = getattr(self.db.root, out_list_name)
            in_list = getattr(self.db.root, in_list_name)
        except:
            print("No swaps currently planned")
            return

        if self.remove_card(card_out, deck=out_list, strict=strict):
            print("Error removing out card, please try again")
            return
        if self.remove_card(card_in, deck=in_list, strict=strict):
            print("Error removing in card, please try again")
            self.add_card(card_out, deck=out_list)
            return

    def execute_swaps(self):
        self.print_planned_swaps(index=True)
        swaps_to_execute_str = input("Enter swaps to execute by index, separated by spaces")
        swaps_to_execute = [int(swap_idx) for swap_idx in swaps_to_execute_str.split(' ')]
        swaps_to_execute.sort(reverse=True)
        for swap in swaps_to_execute:
            #TODO implement
            pass

    def print_planned_swaps(self, index=False):
        #TODO maybe make prettier?
        print()
        out_list_name = f"{self.deck_var_name}_swap_out"
        in_list_name = f"{self.deck_var_name}_swap_in"
        try:
            out_plist = getattr(self.db.root, out_list_name)
            in_plist = getattr(self.db.root, in_list_name)
        except:
            print("No swaps planned")
            return
        
        out_cards = [card.name for card in out_plist.cards]
        in_cards = [card.name for card in in_plist.cards]
        max_len = len(max(out_cards, key = len))
        max_len_in = len(max(in_cards, key = len))
        print(f"{'Swapping out:':{max_len}}\tReplacing with:")
        print(f"="*(max_len+4+max_len_in))
        for i in range(len(out_cards)):
            out_card = out_cards[i]
            in_card = in_cards[i]
            formatted_swap = f'{out_card:{max_len}}\t{in_card:{max_len_in}}'
            if index:
                formatted_swap += f"\t{i}"
            print(formatted_swap)
        print()