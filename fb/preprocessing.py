import json
import csv
from fb.scraper import Reaction


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
    return post['from']['id'], post['topic'], format_text(post['message']), effective


def format_text(text):
    """
    Text prepocessing, such as removing punctuation, possessive 's, and de-capitalization.
    :param story:
    :return:
    """

    return text

    # # Remove punctuation
    # text = text.replace('.', '').replace('?', '').replace(',', '').replace('!', '').replace(':')
    #
    # # # TODO: remove possession?
    # # # Remove possession
    # # story = story.replace("'s", "")
    #
    # # Convert to lower case
    # text = ','.join([word.lower() for word in text.split(' ')])
    # return '[' + text + ']'


def contains(text, keyword):

    # Remove punctuation
    text = text.replace('.', '').replace('?', '').replace(',', '').replace('!', '').replace(':', '').replace('"', '')

    # Split words and convert to lower case
    words = [word.lower() for word in text.split(' ')]

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
        all = sum([val for val in post['reactions'].values()])
        if negative * 1.0 / all < NEG_THRESHOLD:
            effective = True
        else:
            effective = False

    return effective

# with open('fb_data.json') as file:
#     posts = [format_post(post) for post in json.load(file)]

with open('../topics.json') as file:
    topics = json.load(file)
file.close()
posts = search_and_tag('fb_data.json', topics)
posts = [format_post(post) for post in posts]

with open('fb_data.csv', 'w') as file:
    writer = csv.writer(file, delimiter=',', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['author', 'topic', 'text', 'effective'])
    for post in posts:
        writer.writerow(post)

file.close()
