import facebook
import requests
import json
import sys
import time
from enum import Enum
from collections import defaultdict


class FBScraper:

    LIMIT = '25'
    VERSION = 2.6
    FEED = 'feed'

    def __init__(self, app_id, app_secret, access_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.graph = facebook.GraphAPI(access_token=access_token, version=self.VERSION)
        self._posts = []

    # TODO: make asynchronous
    def get_posts(self, page_id, num_posts):

        start = time.time()
        print("Scraping posts for page id=" + str(page_id), end='...')

        # Get posts with total reaction count
        fields = ['message', 'from', 'reactions.limit(0).summary(true)']
        page_posts = self.get_posts_with_fields(page_id, num_posts, fields)

        # Get posts with reaction count by type
        reactions = {}
        for reaction_type in Reaction:
            fields = ['message', 'from', 'reactions.type({0}).limit(0).summary(true)'.format(reaction_type.name)]
            posts_with_reaction_count = self.get_posts_with_fields(page_id, 2 * num_posts, fields)
            counts = {post['id']: post['reactions']['summary']['total_count'] for post in posts_with_reaction_count}
            reactions[reaction_type.name.lower()] = counts
        reactions = self.renest(reactions)

        # Join the posts
        self.join_post_with_reactions(page_posts, reactions)

        end = time.time()
        print(str(len(page_posts)) + ' posts scraped in ' + str(round(end - start, 2)) + ' seconds')

        self._posts.extend(page_posts)

        # Save posts to disk in case of a crash for a particular page
        with open('fb_data.json', 'w') as file:
            json.dump(self.posts, file)

    def get_posts_with_fields(self, page_id, num_posts, fields):

        response = self.graph.get_connections(
            id=page_id, connection_name=self.FEED, limit=self.LIMIT,
            fields=','.join(fields))

        page_posts = [post for post in response['data'] if 'message' in post]

        # Go to the next page of posts
        while len(page_posts) < num_posts and 'paging' in response and 'next' in response['paging']:
            next_url = response['paging']['next']
            response = json.loads(requests.get(next_url).text)
            if 'data' in response:
                page_posts.extend([post for post in response['data'] if 'message' in post])

        return page_posts

    def renest(self, reactions):
        """
        Switches the order of the nesting of reactions dictionary
        http://stackoverflow.com/questions/2273691/pythonic-way-to-reverse-nested-dictionaries
        :param reactions:
        :return:
        """
        flipped = defaultdict(dict)
        for key, val in reactions.items():
            for subkey, subval in val.items():
                flipped[subkey][key] = subval

        return dict(flipped)

    def join_post_with_reactions(self, posts, reactions):
        """
        Joins posts with reaction counts for certain reaction types
        :param posts:
        :param reactions: a nested dictionary. Reaction counts for a given reaction type and post id are accessed
            via reactions[reaction_type][post_id]
        :return:
        """

        for post in posts:
            total_count = post['reactions']['summary']['total_count']
            try:
                post['reactions'] = reactions[post['id']]
            except KeyError:
                print('\nPost ' + post['id'] + ' not in response from reaction count call!\n')
            post['reactions']['all'] = total_count

    @property
    def posts(self):
        return self._posts


class Reaction(Enum):
    # NONE = 1
    LIKE = 2
    LOVE = 3
    WOW = 4
    HAHA = 5
    SAD = 6
    ANGRY = 7
    # THANKFUL = 8


def aggregate(post):
    """
    Aggregates data for a post
    :param post:
    :return:
    """
    if 'message' not in post:
        post['message'] = None

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here

    try:
        app_id = sys.argv[1]
        app_secret = sys.argv[2]
        access_token = sys.argv[3]
        posts_per_page = int(sys.argv[4])

        file = open('pages.csv')
        pages = [row.strip().split(',') for row in file]
        file.close()
        pages = [{'id': page[1], 'name': page[0]} for page in pages]

        scraper = FBScraper(app_id, app_secret, access_token)

        for page in pages:
            scraper.get_posts(page['id'], posts_per_page)

        # Write data to a file
        with open('fb_data.json', 'w') as outfile:
            json.dump(scraper.posts, outfile)

    except IndexError:
        print('Usage: python3 scraper.py <app-id> <app-secret> <access-token> <posts-per-page>')

