from fb.preprocessing import text_to_list
from pymining import itemmining
import csv


MIN_SUP = 0.2
MAX_SUP = 0.05

with open('fb/fb_data.csv') as file:
    reader = csv.reader(file, delimiter=',', escapechar='\\')
    data = [row for row in reader]

header = data[0]
data = data[1:]

# Column indices
author_col = header.index('author')
topic_col = header.index('topic')
text_col = header.index('text')
effective_col = header.index('effective')

# Convert effective column values to bools
for row in data:
    row[effective_col] = row[effective_col] == 'True'

# Split effective posts and ineffective posts
effective_data = [row for row in data if row[effective_col]]
ineffective_data = [row for row in data if not row[effective_col]]

# Convert text to a list of words
effective_text = [text_to_list(row[text_col], True) for row in effective_data]
ineffective_text = [text_to_list(row[text_col], True) for row in ineffective_data]

# Find frequent itemsets in effective posts
relim_input = itemmining.get_relim_input(effective_text)
report = itemmining.relim(relim_input, min_support=int(round(len(effective_text) * MIN_SUP)))
print(report)

# Find frequent itemsets in ineffective posts
relim_input = itemmining.get_relim_input(ineffective_text)
report = itemmining.relim(relim_input, min_support=int(round(len(ineffective_text) * MIN_SUP)))
print(report)

# Throw away frequent itemsets at the intersection
