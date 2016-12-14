import json
import csv
from fb.scraper import Reaction


NEG_THRESHOLD = 0.1


def search(filename, keywords):
    """
    Searches the json file for posts that contain any of the given keywords
    :param filename:
    :param keywords:
    :return:
    """
    matching_posts = []
    with open(filename) as file:
        posts = json.load(file)
        for post in posts:
            if 'message' in post:
                for word in post['message'].split(' '):
                    if word.lower() in keywords:
                        matching_posts.append(post)
                        break
    return matching_posts


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

# with open('fb_data.json') as file:
#     posts = [format_post(post) for post in json.load(file)]

posts = search('fb_data.json', ['abortion'])
posts = [format_post(post) for post in posts]

with open('fb_data.csv', 'w') as file:
    writer = csv.writer(file, delimiter=',', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['author', 'text', 'effective'])
    for post in posts:
        writer.writerow(post)

file.close()
