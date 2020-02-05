import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('../data/pypi_download_counts.csv')

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
        # 0 - 10
        if i < 11:
            a += 1
            continue

        # 11 - 100
        if i >= 11 and i <= 100:
            b += 1
            continue
        
        # 101 - 1,000
        if i >= 101 and i <= 1000:
            c += 1
            continue

        # 1,001 - 10,000
        if i >= 1001 and i <= 10000:
            d += 1
            continue

        # 10,001 - 100,000
        if i >= 10001 and i <= 100000:
            e += 1
            continue

        # 1000001+
        if i > 100001:
            f += 1
            continue

    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(aspect='equal'))

    percentages = [pct(a), pct(b), pct(c), pct(d), pct(e), pct(f)]

    wedges = ax.pie([a, b, c, d, e, f], labels=percentages, shadow=True)[0]

    ax.legend(wedges, ['0 - 10', '11 - 100', '101 - 1,000', '1,001 - 10,000', '10,001 - 100,000', '> 100,000'],
            title='Weekly Download Count',
            loc='center left',
            bbox_to_anchor=(1, 0, 0.5, 1))
            
    ax.set_title('Percentage of PyPI Packages by Weekly Download Count')

    plt.show()

pie()