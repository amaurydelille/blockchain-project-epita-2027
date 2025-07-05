import smartpy as sp

PAYMENT_ERROR="You should pay 1 tez to join a game."
JOIN_ERROR="You already joined the game."
EMPTY_GUESS="You cannot submit an empty guess."
GUESS_ERROR="You cannot submit a guess if you didn't join the game."
GUESS_TWICE_ERROR="You cannot submit more than one guess."
DEADLINE_ERROR="You can neither guess nor join a game after the deadline."
WIN_AMOUNT_ERROR="Only the winner of the game can get the amount of the contract."
WIN_AMOUNT_DEADLINE_ERROR="The amount of the contract can only be earned AFTER the deadline."

def main():
    class GuessSeedGame(sp.Contract):
        def __init__(self, admin, entry_fee, round_duration, deadline):
            self.data.admin = admin
            self.data.entry_fee = entry_fee
            self.data.round_duration = round_duration
            self.data.players = sp.map()
            self.data.deadline = deadline
            self.data.winner = sp.address("") # this field is modified OFF-CHAIN
        
        @sp.entry_point
        def join_game(self):
            assert self.data.deadline > sp.now, DEADLINE_ERROR
            assert sp.amount == self.data.entry_fee, PAYMENT_ERROR
            assert not self.data.players.contains(sp.sender), JOIN_ERROR
            
            self.data.players[sp.sender] = sp.string("")

        @sp.entry_point
        def guess(self, content):
            assert self.data.deadline > sp.now, DEADLINE_ERROR
            assert self.data.players.contains(sp.sender), GUESS_ERROR
            assert self.data.players[sp.sender] == sp.string(""), GUESS_TWICE_ERROR
            assert content != sp.string("")

            self.data.players[sp.sender] = content

        @sp.entry_point
        def reveal(self):
            pass

        @sp.entry_point
        def win_amount(self):
            assert self.data.deadline <= sp.now, WIN_AMOUNT_DEADLINE_ERROR
            assert sp.sender == self.data.winner
            sp.send(self.data.winner, sp.amount)

@sp.add_test
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    sc = sp.test_scenario("Test", main)
    c1 = main.GuessSeedGame(alice, sp.tez(5), sp.timestamp_from_utc(2025, 12, 31, 23, 59, 59))
    sc += 1

    
        

    