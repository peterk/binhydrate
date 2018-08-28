# -*- coding: utf-8 -*-
import unittest
import json
import binhydrate
import os

here = os.path.abspath(os.path.dirname(__file__))

testdata = dict()

with open(os.path.join(here, "testdata_searchres.json")) as f:
    testdata = json.load(f)


class ParseTweet(unittest.TestCase): 

    def test_return_empy_list_parse_binlinks_from_tweet(self):
        empty_tweet = dict()
        result = binhydrate.parse_binlinks_from_tweet(empty_tweet)
        self.assertEqual([], result)


    def test_return_profile_links_for_text_tweet(self):
        sample_tweet = testdata["statuses"][0]
        result = binhydrate.parse_binlinks_from_tweet(sample_tweet)
        self.assertEqual(2, len(result))


    def test_return_video_and_profile_links(self):
        sample_tweet = testdata["statuses"][1]
        result = binhydrate.parse_binlinks_from_tweet(sample_tweet)
        self.assertEqual(4, len(result))


    def test_return_image_tweet_links(self):
        sample_tweet = testdata["statuses"][2]
        result = binhydrate.parse_binlinks_from_tweet(sample_tweet)
        self.assertEqual(3, len(result))


    def test_fetch_urls_to_warc(self):
        sample_tweet = testdata["statuses"][1]
        result = binhydrate.parse_binlinks_from_tweet(sample_tweet)
        binhydrate.fetch_urls_to_warc(result, "test.warc.gz")


if __name__ == '__main__':
    unittest.main()
