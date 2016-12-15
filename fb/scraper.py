import facebook
import requests
import json
import sys
from enum import Enum


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

        print("Scraping posts for page id=" + str(page_id), end='...')

        # fields = ['message', 'from', 'comments.limit({0})'.format(self.LIMIT)]
        fields = ['message', 'from']

        response = self.graph.get_connections(
            id=page_id, connection_name=self.FEED, limit=self.LIMIT,
            fields=','.join(fields))

        page_posts = response['data']

        # Go to the next page of posts
        while len(page_posts) < num_posts and 'paging' in response and 'next' in response['paging']:
            next_url = response['paging']['next']
            response = json.loads(requests.get(next_url).text)
            if 'data' in response:
                page_posts.extend(response['data'])

        # Process the posts (format fields, get additional comments, reactions, etc.)
        for post in page_posts:
            self.process_post(post)

        print(str(len(page_posts)) + ' posts scraped')

        self._posts.extend(page_posts)

    # TODO: Make asynchronous
    def process_post(self, post):

        fields = []
        for reaction_type in Reaction:
            fields.append('reactions.type({0}).limit(0).summary(true).as({0})'.format(
                reaction_type.name))

        response = self.graph.get_object(id=post['id'], fields=','.join(fields))
        post['reactions'] = {}
        for reaction_type in Reaction:
            post['reactions'][reaction_type.name.lower()] = response[reaction_type.name]['summary']['total_count']

        return post

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
    app_id = sys.argv[1]
    app_secret = sys.argv[2]
    access_token = sys.argv[3]
    posts_per_page = sys.argv[4]

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