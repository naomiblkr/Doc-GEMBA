"""
    Calculates absolute and relative frequencies of segment-level scores.
    Assumes you are running the program from score_distribution/ directory.
"""

import pandas as pd
import os
from collections import Counter
import csv


PATH = "../mt-metrics-eval-v2/wmt22/metric-scores/en-de/"
file = os.path.join(PATH, 'doc-GEMBA-SQM_ref_gpt-3.5-turbo-refB.seg.score')
#file = os.path.join(PATH, 'doc-GEMBA-DA_ref_gpt-3.5-turbo-refB.seg.score')

prompt_type = 'doc-GEMBA-SQM_ref'
#prompt_type = 'doc-GEMBA-DA_ref'

col_names=['system-name', 'score'] 

df = pd.read_csv(file, sep='\t', names= col_names, header=None, index_col=None)

scores = df['score'].values.tolist()
n_scores = len(scores)
scores_count = Counter(scores)


with open(prompt_type + '_dis.csv', 'w', encoding='utf-8') as outf:
    writer = csv.writer(outf, delimiter="\t")
    writer.writerow(["Score", "Number of occurrences", "Relative Frequency"])
    for score, n in scores_count.items():
        rel_freq = round((n/n_scores)*100, 2)
        writer.writerow([score, n, rel_freq])