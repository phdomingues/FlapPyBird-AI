import asyncio

from src.game import Game

if __name__ == "__main__":
    asyncio.run(Game(Game.GameMode.PLAY).start())
