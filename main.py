import asyncio

from src.game import Game
from src.train import TrainGA

if __name__ == "__main__":
    #asyncio.run(Game(Game.GameMode.PLAY).start())
    asyncio.run(TrainGA().start())
