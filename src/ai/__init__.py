from pathlib import Path

AI_CONFIG_PATH = Path(__file__).parent.absolute() / 'config.yaml'
BEST_MODEL_PATH = AI_CONFIG_PATH.parent / 'best.pth'