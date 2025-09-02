import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path

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
    fig.tight_layout()
    save_graph('backtesting_results')
    plt.show()

def save_graph(name: str) -> None:
    working_directory = Path(__file__).parent.parent.parent
    graph_file_name = working_directory / 'output' / name
    plt.savefig(graph_file_name)