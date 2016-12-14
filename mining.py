from fb.preprocessing import text_to_list
from pymining import itemmining
import csv


def mine_frequent(transactions, min_freq):

    # Find frequent itemsets in transactions
    input = itemmining.get_relim_input(transactions)
    min_sup = int(round(min_freq * len(transactions)))
    return itemmining.relim(input, min_support=min_sup)


def mine_interesting_and_frequent(transactions, opposing_transactions, min_freq, max_freq):

    # Find frequent itemsets in transactions
    frequent_itemsets = mine_frequent(transactions, min_freq)

    # Find frequent itemsets in opposing set using max_freq as min_freq
    frequent_opposing_itemsets = mine_frequent(opposing_transactions, max_freq)

    return {k: v for k, v in frequent_itemsets.items() if k not in frequent_opposing_itemsets}


# Note: MAX_OPPOSING_FREQ should less than or equal to MIN_FREQ
MIN_FREQ = 0.1
MAX_OPPOSING_FREQ = 0.1

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

# Find frequent itemsets in both sets
frequent_effective = mine_frequent(effective_text, MIN_FREQ)
frequent_ineffective = mine_frequent(ineffective_text, MIN_FREQ)

# Find interesting frequent itemsets
interesting_effective = mine_interesting_and_frequent(effective_text, ineffective_text, MIN_FREQ, MAX_OPPOSING_FREQ)
interesting_ineffective = mine_interesting_and_frequent(ineffective_text, effective_text, MIN_FREQ, MAX_OPPOSING_FREQ)


print('Frequent in effective posts:')
for itemset in frequent_effective:
    print('\t' + str(set(itemset)))

print('Interesting in effective posts:')
for itemset in interesting_effective:
    print('\t' + str(set(itemset)))

print('Frequent in ineffective posts:')
for itemset in frequent_ineffective:
    print('\t' + str(set(itemset)))

print('Interesting in ineffective posts:')
for itemset in interesting_ineffective:
    print('\t' + str(set(itemset)))

# print('Frequent in effective posts:')
# for k, v in frequent_effective.items():
#     print('\t' + str(set(k)) + ':' + str(v))
#
# print('Interesting in effective posts:')
# for k, v in interesting_effective.items():
#     print('\t' + str(set(k)) + ':' + str(v))
#
# print('Frequent in ineffective posts:')
# for k, v in frequent_ineffective.items():
#     print('\t' + str(set(k)) + ':' + str(v))
#
# print('Interesting in ineffective posts:')
# for k, v in interesting_ineffective.items():
#     print('\t' + str(set(k)) + ':' + str(v))
