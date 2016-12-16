import glob
import json


path = "fb_data*.json"
posts = []
for filename in glob.glob(path):
    with open(filename, 'r') as f:
        new_posts = json.load(f)
        posts.extend(new_posts)

with open('fb_data_combined.json', 'w') as f:
    json.dump(posts, f)
