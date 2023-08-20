# Generates download distribution figure for npm

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('../data/npm_download_counts.csv')

download_counts = list(df.weekly_downloads.values)

def pct(value):
    return str(round(value * 100 / len(download_counts) , 1)) + '%'

def pie():
    
    a = 0
    b = 0
    c = 0
    d = 0
    e = 0
    f = 0

    for i in download_counts:
        if i <= 10:
            a += 1
        elif i <= 100:
            b += 1
        elif i <= 1000:
            c += 1
        elif i <= 10000:
            d += 1
        elif i <= 100000:
            e += 1
        else:
            f += 1

    fig, ax = plt.subplots(subplot_kw=dict(aspect='equal'))
    plt.rcParams.update({'font.size': 18})
    percentages = [pct(a), pct(b), pct(c), pct(d), pct(e), pct(f)]

    wedges = ax.pie([a, b, c, d, e, f], labels=percentages, shadow=True)[0]

    ax.legend(wedges, ['0 - 10', '11 - 100', '101 - 1,000', '1,001 - 10,000', '10,001 - 100,000', '> 100,000'],
            title='Weekly Download Count',
            loc='center',
            bbox_to_anchor=(1, 0, 0.5, 1))
            
    plt.show()

pie()