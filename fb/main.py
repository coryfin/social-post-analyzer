import sys
from fb.scraper import FBScraper


app_id = sys.argv[1]
app_secret = sys.argv[2]
access_token = sys.argv[3]

file = open('fb/pages.csv')
pages = [row.strip().split(',') for row in file]
pages = [{'id': page[1], 'name': page[0]} for page in pages]

scraper = FBScraper(app_id, app_secret, access_token)

# Scrape posts from each page
for page in pages:
    # TODO: call asynchronously
    page['posts'] = scraper.get_posts(page['id'])
    print(str(len(page['posts'])) + ' posts scraped')
    print()
    for post in page['posts']:
        if 'message' in post:
            print(post['message'])
        else:
            print('ERR: no message')
