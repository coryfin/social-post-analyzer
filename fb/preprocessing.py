import json
import csv
from fb.scraper import Reaction


NEG_THRESHOLD = 0.1


def format_post(post):

    # Compute effectiveness
    effective = is_effective(post)

    # Format the post
    return post['from']['id'], format_text(post['message']), effective


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


with open('fb_data.json') as file:
    posts = [format_post(post) for post in json.load(file)]


with open('fb_data.csv', 'w') as file:
    writer = csv.writer(file, delimiter=',', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['author', 'text', 'effective'])
    for post in posts:
        writer.writerow(post)

file.close()
