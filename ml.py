from sentence_transformers import SentenceTransformer
import smartpy as sp
import numpy as np
from contract import main
from contract.main import GuessSeedGame

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B" # The latest, smallest and best model possible today.

class Judge:
    """
    This class is used to judge the similarity between the guesses and the original seed.
    We consider that every layer of checking has been done earlier. We assume that all 
    participants and guesses are valid.
    """
    
    def __init__(self, seed: str, contract: GuessSeedGame, model_name: str = MODEL_NAME):
        """
        Initialize the judge with the model.

        Args:
            seed: The original seed.
            model_name: The name of the model to use. By default Qwen3-Embedding-0.6B.
            contract: The contract instance.
        """
        self.model = SentenceTransformer(model_name)
        self.seed = seed
        self.contract = contract

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate the cosine similarity between two vectors.
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def compare(self, guesses: dict[sp.address, str]) -> dict[sp.address, float]:
        """
        Compare the guesses with the seed.

        Args:
            guesses: A dictionary of guesses.

        Returns:
            A dictionary of similarities.
        """
        try:
            seed_embedding = self.model.encode(self.seed)
            guesses_embeddings = {
                address: self.model.encode(guess) for address, guess in guesses.items()
            }

            return {
                address: self._cosine_similarity(seed_embedding, guesses_embeddings[address])
                for address in guesses.keys()
            }

        except Exception as e:
            raise e

    def get_winner(self, similarities: dict[sp.address, float]) -> sp.address:
        """
        Get the winner of the game.
        """
        winner = max(similarities, key=similarities.get)
        self.contract.data.winner = winner
        return winner
    