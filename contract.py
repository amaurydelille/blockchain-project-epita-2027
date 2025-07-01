import smartpy as sp
import sentence_transformers

PAYMENT_ERROR="You should pay 1 tez to join a game."
JOIN_ERROR="You already joined the game."
EMPTY_GUESS="You cannot submit an empty guess."
GUESS_ERROR="You cannot submit a guess if you didn't join the game."
GUESS_TWICE_ERROR="You cannot submit more than one guess."
DEADLINE_ERROR="You can neither guess nor join a game after the deadline."

class GuessSeedGame(sp.Contract):
    def __init__(self, admin, entry_fee, round_duration, deadline):
        self.data.admin = admin
        self.data.entry_fee = entry_fee
        self.data.round_duration = round_duration
        self.data.players = sp.map()
        self.data.deadline = deadline

    @sp.entry_point
    def join_game(self):
        assert self.data.deadline > sp.now, DEADLINE_ERROR
        assert sp.amount == 1, PAYMENT_ERROR
        assert not self.data.players.contains(sp.sender), JOIN_ERROR
        
        self.data.players[sp.sender] = sp.string("")

    @sp.entry_point
    def guess(self, content):
        assert self.data.deadline > sp.now, DEADLINE_ERROR
        assert self.data.players.contains(sp.sender), GUESS_ERROR
        assert self.data.players[sp.sender] == sp.string(""), GUESS_TWICE_ERROR
        assert content != sp.string("")

        self.data.players[sp.sender] = content
        

    
        

    