import matplotlib.pyplot as plt

ENTRY_THRESHOLD = 2

def graph_pair_trades(stock1, stock2, stock1_data, stock2_data, z_score):
    fig = plt.figure()
    start_date = z_score.first_valid_index()
    graph_stocks(fig, stock1, stock2, stock1_data, stock2_data, start_date)
    graph_z_score(fig, z_score, start_date)
    fig.tight_layout()
    plt.show()

def graph_stocks(fig, stock1, stock2, stock1_data, stock2_data, start_date):
    pair_graph = fig.add_subplot(211)
    pair_graph.plot(stock1_data.index, stock1_data.values, label=stock1, color='blue')
    pair_graph.plot(stock2_data.index, stock2_data.values, label=stock2, color='green')
    pair_graph.set_xlim([start_date, stock1_data.index[-1]])
    plt.title("Stock prices")
    plt.legend()
    plt.xticks(rotation=30)

def graph_z_score(fig, z_score, start_date):
    z_score_graph = fig.add_subplot(212)
    z_score_graph.plot(z_score.index, z_score.values, label='Z-Score', color='black')
    z_score_graph.set_xlim([start_date, z_score.index[-1]])
    z_score_graph_bound = z_score.abs().max() * 1.1
    z_score_graph.set_ylim(-z_score_graph_bound, z_score_graph_bound)
    z_score_graph.axhline(0, color='grey', linestyle='--')
    z_score_graph.axhline(ENTRY_THRESHOLD, color='red', linestyle='--')
    z_score_graph.axhline(-ENTRY_THRESHOLD, color='red', linestyle='--')
    plt.title("Z-score")
    plt.xticks(rotation=30)