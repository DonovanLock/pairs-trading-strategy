import matplotlib.pyplot as plt

ENTRY_THRESHOLD = 2

def graph_pair_trades(stock1, stock2, stock1_data, stock2_data, z_score):
    fig = plt.figure()
    graph_stocks(fig, stock1, stock2, stock1_data, stock2_data)
    graph_z_score(fig, z_score)
    fig.subplots_adjust(hspace=0.4)
    plt.show()

def graph_stocks(fig, stock1, stock2, stock1_data, stock2_data):
    pair_graph = fig.add_subplot(211)
    pair_graph.plot(stock1_data.index, stock1_data.values, label=stock1, color='blue')
    pair_graph.plot(stock2_data.index, stock2_data.values, label=stock2, color='green')
    pair_graph.set_xlim([stock1_data.index[0], stock1_data.index[-1]])
    plt.xticks(rotation=30)

def graph_z_score(fig, z_score):
    z_score_graph = fig.add_subplot(212)
    z_score_graph.plot(z_score.index, z_score.values, label='Z-Score', color='black')
    z_score_graph.set_xlim([z_score.index[0], z_score.index[-1]])
    z_score_graph_bound = z_score.abs().max() * 1.1
    z_score_graph.set_ylim(-z_score_graph_bound, z_score_graph_bound)
    z_score_graph.axhline(0, color='yellow', linestyle='--')
    z_score_graph.axhline(ENTRY_THRESHOLD, color='red', linestyle='--')
    z_score_graph.axhline(-ENTRY_THRESHOLD, color='red', linestyle='--')
    plt.xticks(rotation=30)