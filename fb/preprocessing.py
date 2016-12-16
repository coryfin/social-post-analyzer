import json
import csv
import string
from fb.scraper import Reaction
from nltk.corpus import stopwords


NEG_THRESHOLD = 0.1


def search_and_tag(filename, topics):
    """
    Searches the json file for posts that contain any keywords in the given topics and tags them
    :param filename:
    :param topics: a list of topics, represented as a dictionary with entries "tag" and "keywords"
    :return:
    """
    matching_posts = []
    with open(filename) as file:
        posts = json.load(file)
        for post in posts:
            if 'message' in post:
                for topic in topics:
                    if any([contains(post['message'], keyword) for keyword in topic['keywords']]):
                        post['topic'] = topic['tag']
                        matching_posts.append(post)
                        break
    return matching_posts


def format_post(post):

    # Compute effectiveness
    effective = is_effective(post)

    # Format the post
    return post['from']['id'], post['topic'], post['message'], effective


def text_to_list(text, remove_stop_words):
    """
    Converts text to a list of words, with punctuation removed and all words lowercased
    :param text:
    :param remove_stop_words:
    :return:
    """
    # Remove punctuation
    # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    # TODO: remove apostrophe and hyphen?
    text = text.translate(str.maketrans('', '', string.punctuation.replace("'", '').replace('-', '')))

    # Split words and convert to lower case
    words = [word.lower() for word in text.split(' ')]

    if remove_stop_words:
        words = [word for word in words if word not in stopwords.words('english')]

    return words


def contains(text, keyword):

    # Get individual words, lowercased
    words = text_to_list(text, False)

    # Search the text
    try:
        indices = [words.index(x) for x in keyword.split(' ')]
        range_vals = list(range(indices[0], indices[-1] + 1))
        return indices == range_vals
    except ValueError:
        return False


def is_effective(post):
    effective = None
    if 'reactions' in post:
        positive = post['reactions'][Reaction.LIKE.name.lower()] + post['reactions'][Reaction.LOVE.name.lower()]
        negative = post['reactions'][Reaction.ANGRY.name.lower()]
        if 'all' in post['reactions']:
            total_count = post['reactions']
        else:
            total_count = sum([val for key, val in post['reactions'].items() if key != 'all'])
        if negative * 1.0 / total_count < NEG_THRESHOLD:
            effective = True
        else:
            effective = False

    return effective


if __name__ == "__main__":

    # with open('fb_data.json') as file:
    #     posts = [format_post(post) for post in json.load(file)]

    with open('../topics.json') as file:
        topics = json.load(file)
    posts = search_and_tag('fb_data.json', topics)
    posts = [format_post(post) for post in posts]

    with open('fb_data.csv', 'w') as file:
        writer = csv.writer(file, delimiter=',', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['author', 'topic', 'text', 'effective'])
        for post in posts:
            writer.writerow(post)
