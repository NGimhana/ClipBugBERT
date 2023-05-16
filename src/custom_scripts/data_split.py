## split output.jsonl into train, val, and test sets
# train - first 90 lines
# val - pick random 6 lines from train set
# test - last 27 lines

import json
import random

with open('output.jsonl', 'r') as f:
    lines = f.readlines()

train = lines[:90]
val = lines[90:96]
test = lines[96:]

with open('train.jsonl', 'w') as f:
    f.writelines(train)

with open('val.jsonl', 'w') as f:
    f.writelines(val)

with open('test.jsonl', 'w') as f:
    f.writelines(test)


