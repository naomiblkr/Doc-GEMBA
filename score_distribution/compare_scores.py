"""
    Extracts sentences where GEMBA and doc-GEMBA assigned scores with large differences.
    Only scores of DA-based prompts are used.
    Assumes you are running the program from score_distribution/ directory.
"""

import pandas as pd
import os
import json


PATH = "../mt-metrics-eval-v2/wmt22/metric-scores/en-de/"
doc_file = os.path.join(PATH, 'doc-GEMBA-DA_ref_gpt-3.5-turbo-refB.seg.score')
sent_file = os.path.join(PATH, 'sent-GEMBA_DA_ref_gpt-3.5-turbo-refB.seg.score')

col_names=['system-name', 'score'] 

df_doc = pd.read_csv(doc_file, sep='\t', names=col_names, header=None, index_col=None)
df_sent = pd.read_csv(sent_file, sep='\t', names=col_names, header=None, index_col=None)

scores_doc = list(df_doc.to_records())
scores_sent = list(df_sent.to_records())

# make sure there is an equal number of segment scores
assert len(scores_doc) == len(scores_sent)

differences = []

# system idx starts from 0 per system
sys_idx = 0
sys = scores_doc[0][1]
for (doc_idx, doc_sys, doc_score), (sent_idx, sent_sys, sent_score) in zip(scores_doc, scores_sent):
    # increase index if still the same system
    if doc_sys == sys:
        sys_idx += 1
    # if new system, set index to 0
    else:
        sys = doc_sys
        sys_idx = 0
    # get sentences where score differs by 40 or more
    diff = abs(doc_score - sent_score)
    if diff >= 40:
    #if diff == 25:
        differences.append((diff, doc_score, sent_score, doc_sys, sys_idx))

#print(differences)

path_sys_output = '../mt-metrics-eval-v2/wmt22/system-outputs/en-de/'
path_src = '../mt-metrics-eval-v2/wmt22/sources/en-de.txt'

json_data = []

# count how many times doc-score is higher than sent-score
count = 0

# extract sentences from system outputs
for (diff, doc_score, sent_score, sys_name, idx) in differences:
    sys_output_f = os.path.join(path_sys_output, sys_name + '.txt')
    if doc_score > sent_score:
        count += 1
    with open(sys_output_f, 'r', encoding='utf-8') as sys_f,\
          open(path_src, 'r', encoding='utf-8') as src_f:
        sys_output = [line.rstrip() for line in sys_f]
        src = [line.rstrip() for line in src_f]
        assert len(sys_output) == len(src)
        prev_sents = ' '.join(sys_output[idx-2:idx])
        sent = sys_output[idx]
        src_prev_sents = ' '.join(src[idx-2:idx])
        src_sent = src[idx]
        diff_dict = {'score_diff': int(diff), 'doc_score': int(doc_score), 'sent_score': int(sent_score), \
                'hyp_context': prev_sents, 'hyp_sent': sent, 'src_context': src_prev_sents, 'src_sent': src_sent}
        json_data.append(diff_dict)


print(f'Number of sentences with scoring difference: {len(differences)}')
print(f'Number of times doc-score is higher than sent-score: {count}')

with open('sents_scoring_diff.json', 'w', encoding='utf-8') as outf:
    json.dump(json_data, outf, ensure_ascii=False)