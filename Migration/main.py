from cleaner import DataCleaner
from transformer import SabermetricsCalculator
import pandas as pd


def main():
    cleaner = DataCleaner()
    calculator = SabermetricsCalculator()
    player = cleaner.load_player_stats()
    league = cleaner.load_league_stats()
main()