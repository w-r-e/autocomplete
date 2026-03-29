import dawg
import trie
import radix_tree
from main import load_words, dawg_setup, trie_setup, radix_tree_setup
from plotly import graph_objects as graph
import random
import timeit

NUM_RUNS = 5


def tester(words, sizes):
    results = {
        'trie': {'sizes': [], 'memory': [], 'setup_time': [], 'query_time': []},
        'radix': {'sizes': [], 'memory': [], 'setup_time': [], 'query_time': []},
        'dawg': {'sizes': [], 'memory': [], 'setup_time': [], 'query_time': []}
    }
    test_prefixes = []
    prefix_source = random.choices(words, k=100)

    for word, _ in prefix_source:
        for length in range(2, 5):
            if len(word) > length:
                test_prefixes.append(word[:length])
    test_prefixes = list(set(test_prefixes))[:50]

    for size in sizes:
        trie_result = trie_tester(size, words, test_prefixes)
        radix_result = radix_tester(size, words, test_prefixes)
        dawg_result = dawg_tester(size, words, test_prefixes)

        results['trie']['sizes'].extend(trie_result['sizes'])
        results['trie']['memory'].extend(trie_result['memory'])
        results['trie']['setup_time'].extend(trie_result['setup_time'])
        results['trie']['query_time'].extend(trie_result['query_time'])

        results['radix']['sizes'].extend(radix_result['sizes'])
        results['radix']['memory'].extend(radix_result['memory'])
        results['radix']['setup_time'].extend(radix_result['setup_time'])
        results['radix']['query_time'].extend(radix_result['query_time'])

        results['dawg']['sizes'].extend(dawg_result['sizes'])
        results['dawg']['memory'].extend(dawg_result['memory'])
        results['dawg']['setup_time'].extend(dawg_result['setup_time'])
        results['dawg']['query_time'].extend(dawg_result['query_time'])

    return results


def trie_tester(size, words, test_prefixes):
    results = {"sizes": [], "memory": [], "setup_time": [], "query_time": []}

    trimmed_words = words[:size]

    trie_setup_time = timeit.timeit(
        lambda: trie_setup(trimmed_words),
        number=NUM_RUNS
    ) / NUM_RUNS

    trie = trie_setup(trimmed_words)
    trie_memory = trie.get_total_memory()

    def query_trie():
        for prefix in test_prefixes:
            trie.search(prefix, k=10)

    trie_query_time = timeit.timeit(query_trie, number=NUM_RUNS) / (NUM_RUNS * len(test_prefixes))

    results['sizes'].append(size)
    results['memory'].append(trie_memory)
    results['setup_time'].append(trie_setup_time)
    results['query_time'].append(trie_query_time)

    return results


def radix_tester(size, words, test_prefixes):
    results = {"sizes": [], "memory": [], "setup_time": [], "query_time": []}

    trimmed_words = words[:size]

    radix_setup_time = timeit.timeit(
        lambda: radix_tree_setup(trimmed_words),
        number=NUM_RUNS
    ) / NUM_RUNS

    radix = radix_tree_setup(trimmed_words)
    radix_memory = radix.get_total_memory()

    def query_radix():
        for prefix in test_prefixes:
            radix.search(prefix, k=10)

    radix_query_time = timeit.timeit(query_radix, number=NUM_RUNS) / (NUM_RUNS * len(test_prefixes))

    results['sizes'].append(size)
    results['memory'].append(radix_memory)
    results['setup_time'].append(radix_setup_time)
    results['query_time'].append(radix_query_time)

    return results


def dawg_tester(size, words, test_prefixes):
    results = {"sizes": [], "memory": [], "setup_time": [], "query_time": []}

    trimmed_words = words[:size]

    dawg_setup_time = timeit.timeit(
        lambda: dawg_setup(trimmed_words),
        number=NUM_RUNS
    ) / NUM_RUNS

    dawg = dawg_setup(trimmed_words)
    dawg_memory = dawg.get_total_memory()

    def query_dawg():
        for prefix in test_prefixes:
            dawg.search(prefix, k=10)

    dawg_query_time = timeit.timeit(query_dawg, number=NUM_RUNS) / (NUM_RUNS * len(test_prefixes))

    results['sizes'].append(size)
    results['memory'].append(dawg_memory)
    results['setup_time'].append(dawg_setup_time)
    results['query_time'].append(dawg_query_time)

    return results


def plot_MB_size(results):
    fig = graph.Figure()

    fig.add_trace(graph.Scatter(
        x=results['trie']['sizes'],
        y=[m / (1024 ** 2) for m in results['trie']['memory']],
        mode='lines+markers',
        name='Trie',
        line=dict(color='red', width=3),
        marker=dict(size=8, symbol='circle')
    ))

    fig.add_trace(graph.Scatter(
        x=results['radix']['sizes'],
        y=[m / (1024 ** 2) for m in results['radix']['memory']],
        mode='lines+markers',
        name='Radix Tree',
        line=dict(color='blue', width=3),
        marker=dict(size=8, symbol='square')
    ))

    fig.add_trace(graph.Scatter(
        x=results['dawg']['sizes'],
        y=[m / (1024 ** 2) for m in results['dawg']['memory']],
        mode='lines+markers',
        name='DAWG',
        line=dict(color='green', width=3),
        marker=dict(size=8, symbol='diamond')
    ))

    fig.update_layout(
        title='Memory Usage vs Dataset Size',
        xaxis_title='Number of Words',
        yaxis_title='Memory (MB)',
        hovermode='x unified',
        font=dict(size=14),
        width=900,
        height=600,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)')
    )

    return fig


def plot_setup_size(results):
    """Graph 2: Setup Time vs Dataset Size"""

    fig = graph.Figure()

    fig.add_trace(graph.Scatter(
        x=results['trie']['sizes'],
        y=results['trie']['setup_time'],
        mode='lines+markers',
        name='Trie',
        line=dict(color='red', width=3),
        marker=dict(size=8, symbol='circle')
    ))

    fig.add_trace(graph.Scatter(
        x=results['radix']['sizes'],
        y=results['radix']['setup_time'],
        mode='lines+markers',
        name='Radix Tree',
        line=dict(color='blue', width=3),
        marker=dict(size=8, symbol='square')
    ))

    fig.add_trace(graph.Scatter(
        x=results['dawg']['sizes'],
        y=results['dawg']['setup_time'],
        mode='lines+markers',
        name='DAWG',
        line=dict(color='green', width=3),
        marker=dict(size=8, symbol='diamond')
    ))

    fig.update_layout(
        title='Setup Time vs Dataset Size',
        xaxis_title='Number of Words',
        yaxis_title='Setup Time (seconds)',
        hovermode='x unified',
        font=dict(size=14),
        width=900,
        height=600,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)')
    )

    return fig


def plot_query_size(results):
    """Graph 3: Average Query Time vs Dataset Size (in milliseconds)"""

    fig = graph.Figure()

    fig.add_trace(graph.Scatter(
        x=results['trie']['sizes'],
        y=[t * 1000 for t in results['trie']['query_time']],
        mode='lines+markers',
        name='Trie',
        line=dict(color='red', width=3),
        marker=dict(size=8, symbol='circle')
    ))

    fig.add_trace(graph.Scatter(
        x=results['radix']['sizes'],
        y=[t * 1000 for t in results['radix']['query_time']],
        mode='lines+markers',
        name='Radix Tree',
        line=dict(color='blue', width=3),
        marker=dict(size=8, symbol='square')
    ))

    fig.add_trace(graph.Scatter(
        x=results['dawg']['sizes'],
        y=[t * 1000 for t in results['dawg']['query_time']],
        mode='lines+markers',
        name='DAWG',
        line=dict(color='green', width=3),
        marker=dict(size=8, symbol='diamond')
    ))

    fig.update_layout(
        title='Average Query Time vs Dataset Size',
        xaxis_title='Number of Words',
        yaxis_title='Query Time (milliseconds)',
        hovermode='x unified',
        font=dict(size=14),
        width=900,
        height=600,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)')
    )

    return fig

def grapher_main(file):
    words = load_words(file)
    sizes = [1000, 10000, 50000, 100000, 150000, 200000, 250000, 300000]
    results = tester(words, sizes)

    fig_memory = plot_MB_size(results)
    fig_memory.write_html("memory_vs_size.html")
    fig_memory.show()

    fig_setup = plot_setup_size(results)
    fig_setup.write_html("setup_time_vs_size.html")
    fig_setup.show()

    fig_query = plot_query_size(results)
    fig_query.write_html("query_time_vs_size.html")
    fig_query.show()

    return results

if __name__ == "__main__":
    results = grapher_main("unigram_freq.csv")

# TODO: Wait move all setups to each implement???
