import smartpy as sp

PAYMENT_ERROR="You should pay 1 tez to join a game."
JOIN_ERROR="You already joined the game."
EMPTY_GUESS="You cannot submit an empty guess."
GUESS_ERROR="You cannot submit a guess if you didn't join the game."
GUESS_TWICE_ERROR="You cannot submit more than one guess."
DEADLINE_ERROR="You can neither guess nor join a game after the deadline."
WIN_AMOUNT_ERROR="Only the winner of the game can get the amount of the contract."
WIN_AMOUNT_DEADLINE_ERROR="The amount of the contract can only be earned AFTER the deadline."
REVEAL_DEADLINE_ERROR="You can only reveal the winner after the deadline."
ADMIN_ERROR="Only the admin can perform this action."

@sp.module
def main():

    class GuessSeedGame(sp.Contract):
        def __init__(self, admin, entry_fee, deadline):
            self.data.admin = admin
            self.data.entry_fee = entry_fee
            self.data.players = sp.map()
            self.data.deadline = deadline
            self.data.winner = sp.address("") 
            self.data.seed = sp.string("")
            self.data.generated_images = sp.map()
        

        @sp.entry_point
        def init_game(self, seed, deadline):
            assert sp.sender == self.data.admin, ADMIN_ERROR
            self.data.seed = seed
            self.data.players.clear()
            self.data.winner = sp.address("")
            self.data.seed = sp.string("")
            # call api to set generated_images
            self.data.deadline = deadline

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
            assert content != sp.string(""), EMPTY_GUESS

            self.data.players[sp.sender] = content

        @sp.entry_point
        def reveal(self):
            assert self.data.deadline <= sp.now, REVEAL_DEADLINE_ERROR
            #call api to set winner
            

        @sp.entry_point
        def win_amount(self):
            assert self.data.deadline <= sp.now, WIN_AMOUNT_DEADLINE_ERROR
            assert sp.sender == self.data.winner, WIN_AMOUNT_ERROR
            sp.send(self.data.winner, sp.balance)
            self.data.players.clear()
            self.data.winner = sp.address("")
            self.data.seed = sp.string("")
            self.data.generated_images.clear()

@sp.add_test()
def test():
    scenario = sp.test_scenario("Guess Seed Game Test", main)
    
    admin = sp.test_account("Admin")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    other = sp.test_account("Other")
    
    entry_fee = sp.tez(1)
    deadline = sp.timestamp(2000000)
    
    contract = main.GuessSeedGame(admin.address, entry_fee, deadline)
    scenario += contract
    
    # Test initial state
    scenario.verify(contract.data.admin == admin.address)
    scenario.verify(contract.data.entry_fee == entry_fee)
    scenario.verify(contract.data.deadline == deadline)
    scenario.verify(contract.data.seed == sp.string(""))
    scenario.verify(contract.data.winner == sp.address(""))
    
    # Test init_game - only admin can set seed
    contract.init_game("test_seed", deadline, _sender=other.address, _valid=False, _exception=ADMIN_ERROR)
    
    contract.init_game("test_seed", deadline, _sender=admin.address)
    scenario.verify(contract.data.seed == "test_seed")
    
    # Wrong payment amount
    contract.join_game(_sender=alice.address, _amount=sp.tez(2), _now=sp.timestamp(1000000), _valid=False, _exception=PAYMENT_ERROR)
    
    # Correct payment
    contract.join_game(_sender=alice.address, _amount=entry_fee, _now=sp.timestamp(1000000))
    scenario.verify(contract.data.players.contains(alice.address))
    scenario.verify(contract.data.players[alice.address] == sp.string(""))
    
    # Try to join twice
    contract.join_game(_sender=alice.address, _amount=entry_fee, _now=sp.timestamp(1000000), _valid=False, _exception=JOIN_ERROR)
    
    # Bob joins
    contract.join_game(_sender=bob.address, _amount=entry_fee, _now=sp.timestamp(1000000))
    scenario.verify(contract.data.players.contains(bob.address))
    
    # Test join_game after deadline
    contract.join_game(_sender=eve.address, _amount=entry_fee, _now=sp.timestamp(3000000), _valid=False, _exception=DEADLINE_ERROR)
    
    # Player must join first
    contract.guess("my guess", _sender=eve.address, _now=sp.timestamp(1000000), _valid=False, _exception=GUESS_ERROR)
    
    # Test empty guess
    contract.guess(sp.string(""), _sender=alice.address, _now=sp.timestamp(1000000), _valid=False, _exception=EMPTY_GUESS)
    
    # Valid guess
    contract.guess("alice's guess", _sender=alice.address, _now=sp.timestamp(1000000))
    scenario.verify(contract.data.players[alice.address] == "alice's guess")
    
    # Try to guess twice
    contract.guess("alice's second guess", _sender=alice.address, _now=sp.timestamp(1000000), _valid=False, _exception=GUESS_TWICE_ERROR)
    
    # Bob's guess
    contract.guess("bob's guess", _sender=bob.address, _now=sp.timestamp(1000000))
    scenario.verify(contract.data.players[bob.address] == "bob's guess")
    
    # Test guess after deadline
    contract.guess("late guess", _sender=alice.address, _now=sp.timestamp(3000000), _valid=False, _exception=DEADLINE_ERROR)
    
    # Test reveal before deadline
    contract.reveal(_sender=admin.address, _now=sp.timestamp(1000000), _valid=False, _exception=REVEAL_DEADLINE_ERROR)
    
    # Test reveal after deadline
    contract.reveal(_sender=admin.address, _now=sp.timestamp(3000000))
    
    # Manually set winner for testing win_amount (in real scenario, this would be done by the reveal function)
    scenario.verify(contract.data.winner == sp.address(""))  # Winner not set yet in this implementation
    
    # Test win_amount before deadline
    contract.win_amount(_sender=alice.address, _now=sp.timestamp(1000000), _valid=False, _exception=WIN_AMOUNT_DEADLINE_ERROR)
    
    # Test win_amount by non-winner after deadline (this will fail because winner is not set)
    contract.win_amount(_sender=bob.address, _now=sp.timestamp(3000000), _valid=False, _exception=WIN_AMOUNT_ERROR)
    
    # Note: In a complete implementation, the reveal function would set the winner
    # and then the winner could call win_amount to get the contract balance
    
    # Test reset functionality when setting new seed
    new_deadline = sp.timestamp(3000000)
    contract.init_game("new_seed", new_deadline, _sender=admin.address)
    scenario.verify(contract.data.seed == "new_seed")
    scenario.verify(contract.data.winner == sp.address(""))
    # Players map should be cleared
    scenario.verify(~contract.data.players.contains(alice.address))
    scenario.verify(~contract.data.players.contains(bob.address))

    
        

    