import facebook
import requests
import json
from enum import Enum


class FBScraper:

    POSTS_PER_PAGE = 100
    LIMIT = '25'
    VERSION = 2.6
    FEED = 'feed'

    def __init__(self, app_id, app_secret, access_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.graph = facebook.GraphAPI(access_token=access_token, version=self.VERSION)

    # TODO: make asynchronous
    def get_posts(self, page_id):

        response = self.graph.get_connections(
            id=page_id, connection_name=self.FEED, limit=self.LIMIT,
            fields='message,comments.limit(' + self.LIMIT + '),reactions.limit(' + self.LIMIT + ')')

        # Process the posts (format fields, get additional comments, reactions, etc.)
        posts = [self.process_post(post) for post in response['data']]

        # Go to the next page of posts
        while len(posts) < self.POSTS_PER_PAGE and 'paging' in response and 'next' in response['paging']:
            next_url = response['paging']['next']
            response = json.loads(requests.get(next_url).text)
            if 'data' in response:
                posts.extend([self.process_post(post) for post in response['data']])

        return posts

    # TODO: Make asynchronous
    def process_post(self, post):

        if post['comments']:
            comments_paging = post['comments']['paging']
            post['comments'] = post['comments']['data']

            # TODO: Call asynchronously
            # # Go to next page of comments
            # while 'next' in comments_paging:
            #     next_url = comments_paging['next']
            #     response = json.loads(requests.get(next_url).text)
            #     if 'data' in response:
            #         post['comments'].extend(response['data'])
            #     if 'paging' in response:
            #         comments_paging = response['paging']
            #     else:
            #         comments_paging = {}

        if post['reactions']:
            reactions_paging = post['reactions']['paging']
            post['reactions'] = post['reactions']['data']

            # TODO: Call asynchronously
            # # Go to next page of reactions
            # while 'next' in reactions_paging:
            #     next_url = reactions_paging['next']
            #     response = json.loads(requests.get(next_url).text)
            #     if 'data' in response:
            #         post['reactions'].extend(response['data'])
            #     if 'paging' in response:
            #         reactions_paging = response['paging']
            #     else:
            #         reactions_paging = {}

        aggregate(post)

        return post


class Reaction(Enum):
    NONE = 1
    LIKE = 2
    LOVE = 3
    WOW = 4
    HAHA = 5
    SAD = 6
    ANGRY = 7
    THANKFUL = 8


def aggregate(post):
    """
    Aggregates data for a post
    :param post:
    :return:
    """

    # Count the number of comments
    if post['comments']:
        post['comment_count'] = len(post['comments'])

    # Count the number of each reaction type
    if post['reactions']:
        post['reaction_counts'] = {}
        for reaction in post['reactions']:
            type = reaction['type']
            if type in post['reaction_counts']:
                post['reaction_counts'][type] += 1
            else:
                post['reaction_counts'][type] = 0
