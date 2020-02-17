import typosquatting_transitive
import pandas as pd

df = pd.read_csv('../data/npm_download_counts.csv')

for package in list(df.package_name.values):
    