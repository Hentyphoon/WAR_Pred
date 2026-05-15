from cleaner import DataCleaner
from transformer import SabermetricsCalculator
import pandas as pd


def main():
    cleaner = DataCleaner()
    calculator = SabermetricsCalculator()
    cleaner.load_player_stats()