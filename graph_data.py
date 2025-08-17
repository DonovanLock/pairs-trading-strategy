from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from config import ENTRY_THRESHOLD, EXIT_THRESHOLD

def graph_backtesting(backtesting_results: pd.DataFrame) -> None:
    fig = plt.figure()
    capital_graph = fig.add_subplot(111)
    capital_graph.plot(backtesting_results.index, backtesting_results['Capital'], label='Capital', color='blue')
    capital_graph.set_title('Backtesting Results')
    capital_graph.set_xlabel('Date')
    capital_graph.set_ylabel('Capital')
    capital_graph.set_xlim([backtesting_results.index[0], backtesting_results.index[-1]])

    entry_signals_filter = backtesting_results['Entries'] > 0
    exit_signals_filter = backtesting_results['Exits'] > 0
    capital_graph.scatter(backtesting_results['Entries'][entry_signals_filter].index, backtesting_results['Capital'][entry_signals_filter], marker='+', color='green', label='Entry Signal', alpha=0.5)
    capital_graph.scatter(backtesting_results['Exits'][exit_signals_filter].index, backtesting_results['Capital'][exit_signals_filter], marker='+', color='red', label='Exit Signal', alpha=0.5)
    plt.xticks(rotation=30)
    plt.legend()
    save_graph('backtesting_results')
    plt.show()

def graph_pair_trade(stock1: str, stock2: str, pair_data: pd.DataFrame) -> None:
    fig = plt.figure()
    z_score = pair_data['Z-score']
    start_date = z_score.first_valid_index()
    graph_stocks(fig, stock1, stock2, pair_data, start_date)
    graph_z_score(fig, z_score, start_date)
    graph_capital(fig, pair_data, start_date)
    fig.tight_layout()
    save_graph(f'graphs_{stock1}_{stock2}')

def graph_stocks(fig: Figure, stock1: str, stock2: str, pair_data: pd.DataFrame, start_date: pd.Timestamp) -> None:
    pair_graph = fig.add_subplot(311)
    pair_graph.plot(pair_data[stock1].index, pair_data[stock1].values, label=stock1, color='blue')
    pair_graph.plot(pair_data[stock2].index, pair_data[stock2].values, label=stock2, color='orange')
    pair_graph.set_xlim([start_date, pair_data[stock1].index[-1]])
    plt.title('Stock prices')
    plt.legend()
    plt.xticks(rotation=30)

def graph_z_score(fig: Figure, z_score: pd.Series, start_date: pd.Timestamp) -> None:
    z_score_graph = fig.add_subplot(312)
    z_score_graph.set_xlim([start_date, z_score.index[-1]])
    z_score_graph_bound = z_score.abs().max() * 1.1
    z_score_graph.set_ylim(-z_score_graph_bound, z_score_graph_bound)
    z_score_graph.axhline(EXIT_THRESHOLD, color='grey', linestyle='--')
    if EXIT_THRESHOLD > 0:
        z_score_graph.axhline(-EXIT_THRESHOLD, color='grey', linestyle='--')
    z_score_graph.axhline(ENTRY_THRESHOLD, color='red', linestyle='--')
    z_score_graph.axhline(-ENTRY_THRESHOLD, color='red', linestyle='--')
    z_score_graph.plot(z_score.index, z_score.values, label='Z-Score', color='black')
    plt.title('Z-score')
    plt.xticks(rotation=30)

def graph_capital(fig: Figure, pair_data: pd.DataFrame, start_date: pd.Timestamp) -> None:
    capital_graph = fig.add_subplot(313)
    capital = pair_data['Capital']
    capital_graph.plot(capital.index, capital.values, label='Capital', color='green')
    capital_graph.set_xlim([start_date, capital.index[-1]])
    plt.title('Capital')
    plt.xticks(rotation=30)

def save_graph(name: str) -> None:
    working_directory = Path(__file__).parent
    graph_file_name = working_directory / 'output' / name
    plt.savefig(graph_file_name)