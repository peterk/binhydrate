# -*- coding: utf-8 -*-
import json
import pprint
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import requests

pp = pprint.PrettyPrinter(indent=4)

def parse_extended_entities(extended_entities_dict):
    """Parse media file URL:s form tweet data

    :extended_entities_dict: 
    :returns: list of media file urls

    """
    urls = []
    
    if "media" in extended_entities_dict.keys():
        for item in extended_entities_dict["media"]:

            #add static image
            urls.append(item["media_url_https"])

            # add best quality video file
            if "video_info" in item.keys():
                max_bitrate = -1 # handle twitters occasional bitrate=0
                video_url = None
                for video in item["video_info"]["variants"]:
                    if "bitrate" in video.keys() and "content_type" in video.keys():
                        if video["content_type"] == "video/mp4":
                            if int(video["bitrate"]) > max_bitrate:
                                max_bitrate = int(video["bitrate"])
                                video_url = video["url"]
                
                if not video_url:
                    print("Error: No bitrate / content_type")
                    pp.pprint(item["video_info"])
                else:
                    urls.append(video_url)

    return urls



def parse_binlinks_from_tweet(tweetdict):
    """Parse binary file url:s from a single tweet.

    :tweetdict: json data dict for tweet
    :returns: list of urls for media files

    """
    
    urls = []

    if "user" in tweetdict.keys():
        urls.append(tweetdict["user"]["profile_image_url_https"])
        urls.append(tweetdict["user"]["profile_background_image_url_https"])

    if "extended_entities" in tweetdict.keys():
        urls.extend(parse_extended_entities(tweetdict["extended_entities"]))
    return urls



def fetch_urls_to_warc(urls, warcfile_path):
    """Fetch urls and write to warc file

    :urls: list of urls to binary files
    :warcfile_path: path to a WARC file.

    """

    with open(warcfile_path, 'wb') as output:
        writer = WARCWriter(output, gzip=True)

        for url in urls:
            print(url)
            resp = requests.get(url, headers={'Accept-Encoding': 'identity'}, stream=True)

            headers_list = resp.raw.headers.items()
            http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')
            record = writer.create_warc_record(url, 'response',
                                                payload=resp.raw,
                                                http_headers=http_headers)
            writer.write_record(record)



def fetch_binlinks_for_tweets(tweetfile_path, warcfile_path):
    """Fetch urls to binary files from twitter data in line oriented json file. Write to warc file.
    """
    urls = []

    with open(tweetfile_path, 'r') as tweetfile:
        for line in tweetfile:
            #print("------------------------------------")
            #print(line)
            tweet = json.loads(line)

            tweet_urls = parse_binlinks_from_tweet(tweet)

            for url in tweet_urls:
                if not url in urls:
                    urls.append(url)
    fetch_urls_to_warc(urls, warcfile_path)
    return urls 
