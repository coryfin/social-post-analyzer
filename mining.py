from fb.preprocessing import text_to_list, clean_twitter_text
from pymining import itemmining
import csv
import sys
import copy


def mine_frequent(transactions, min_sup):

    # Find frequent itemsets in transactions
    input = itemmining.get_relim_input(transactions)
    min_sup_count = int(round(min_sup * len(transactions)))
    return itemmining.relim(input, min_support=min_sup_count)


def mine_interesting_and_frequent(transactions, contrasting_transactions, min_sup, max_sup):

    # Find frequent itemsets in transactions
    frequent_itemsets = mine_frequent(transactions, min_sup)

    # Count frequency in contrasting set
    max_sup_count = int(round(max_sup * len(contrasting_transactions)))
    contrasting_count = {}
    for itemset in frequent_itemsets:
        contrasting_matches = [row for row in contrasting_transactions if contains(row, itemset)]
        contrasting_count[itemset] = len(contrasting_matches)

    return {k: v for k, v in frequent_itemsets.items() if contrasting_count[k] < max_sup_count}


def contains(transaction, itemset):
    """
    Returns True if the transaction contains the itemset
    :param transaction:
    :param itemset:
    :return:
    """
    return all([item in transaction for item in itemset])


def uniquify(items):
    items = copy.deepcopy(items)
    counts = {}
    for i in range(len(items)):
        if items[i] in counts:
            counts[items[i]] += 1
            items[i] = items[i] + '_' + str(counts[items[i]] - 1)
        else:
            counts[items[i]] = 1

    return items


if __name__ == "__main__":

    try:
        data_file = sys.argv[1]
        param = sys.argv[2]
        effectiveness_threshold = float(param)

        # Note: MAX_OPPOSING_FREQ should less than or equal to MIN_FREQ
        min_sup = float(sys.argv[3])
        max_sup = float(sys.argv[4])

        # noinspection PyUnboundLocalVariable
        if max_sup > min_sup:
            print('<max-sup> must be less than or equal to <min-sup>')
        else:

            with open(data_file) as file:
                reader = csv.reader(file, delimiter=',', escapechar='\\')
                data = [row for row in reader]

            header = data[0]
            data = data[1:]

            for row in data:
                if len(row) > 3:
                    print(str(row))

            # Handles two cases:
            # 1. 'effective' attribute is given
            # 2. 'effectiveness' attribute is given and must be compared to threshold to label as effective or ineffective
            if 'effective' not in header:

                header.append('effective')
                effectiveness_col = header.index('effectiveness')

                # Label each data point as effective or ineffective
                for row in data:
                    if row[effectiveness_col] == '':
                        effective = None
                    else:
                        effective = float(row[effectiveness_col]) >= effectiveness_threshold
                    row.append(effective)
            else:
                effective_col = header.index('effective')
                for row in data:
                    if row[effective_col] == 'True' or row[effective_col] == 'T':
                        row[effective_col] = True
                    elif row[effective_col] == 'False' or row[effective_col] == 'F':
                        row[effective_col] = False
                    else:
                        row[effective_col] = None

            # Column indices
            # author_col = header.index('author')
            # topic_col = header.index('topic')
            text_col = header.index('text')
            effective_col = header.index('effective')

            # Split effective posts and ineffective posts
            effective_data = [row for row in data if row[effective_col]]
            ineffective_data = [row for row in data if not row[effective_col]]

            if 'twitter' in data_file:
                # Convert text to a list of words
                effective_text = [uniquify(text_to_list(clean_twitter_text(row[text_col]), True)) for row in effective_data]
                ineffective_text = [uniquify(text_to_list(clean_twitter_text(row[text_col]), True)) for row in ineffective_data]
            else:
                # Convert text to a list of words
                effective_text = [uniquify(text_to_list(row[text_col], True)) for row in effective_data]
                ineffective_text = [uniquify(text_to_list(row[text_col], True)) for row in ineffective_data]

            # Find frequent itemsets in both sets
            frequent_effective = mine_frequent(effective_text, min_sup)
            frequent_ineffective = mine_frequent(ineffective_text, min_sup)

            # Find interesting frequent itemsets
            interesting_effective = mine_interesting_and_frequent(effective_text, ineffective_text, min_sup, max_sup)
            interesting_ineffective = mine_interesting_and_frequent(ineffective_text, effective_text, min_sup, max_sup)

            print('file=' + data_file)
            print('threshold=' + str(effectiveness_threshold) + ',min_sup=' + str(min_sup) + ',max_sup=' + str(max_sup))
            print()

            print('Frequent in effective posts:')
            for k, v in frequent_effective.items():
                print(str(set(k)) + ':' + str(v) + ',' + str(round(v / len(effective_data), 4)))
            print()

            print('Interesting in effective posts:')
            for k, v in interesting_effective.items():
                print(str(set(k)) + ':' + str(v) + ',' + str(round(v / len(effective_data), 4)))
            print()

            print('Frequent in ineffective posts:')
            for k, v in frequent_ineffective.items():
                print(str(set(k)) + ':' + str(v) + ',' + str(round(v / len(ineffective_data), 4)))
            print()

            print('Interesting in ineffective posts:')
            for k, v in interesting_ineffective.items():
                print(str(set(k)) + ':' + str(v) + ',' + str(round(v / len(ineffective_data), 4)))

    except ValueError:
        print('usages:')
        print('\tpython3 mining.py <effectiveness-threshold> <min-sup> <max-sup>')
