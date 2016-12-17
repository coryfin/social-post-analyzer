# social-post-analyzer

To run this code, you must install the following modules:
 1. pymining
 2. nltk
 3. facebook-sdk

If you have pip, this is simple. Run:
$ pip install pymining
$ pip install nltk

You also need the english corpus for nltk. Download this with the following command:
$ python3 download_stopwords.py

This will open a download dialog. Click on the "Corpora" tab and use the scroll bar on the right to scroll down to
the stopwords corpus, which you will select and click download.

Now you can run the code. To mine patterns, run the following command:
$ python3 mining.py <dataset> <effectiveness-threshold> <min-sup-a> <min-sup-b>
