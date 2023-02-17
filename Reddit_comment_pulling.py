# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:24:54 2021

@author: pscha
"""
import requests
from datetime import datetime, timedelta
import traceback
import time
import json
import sys
import os

username = ""  # put the username you want to download in the quotes
subreddit = "Work*Right*"  # put the subreddit you want to download in the quotes
# leave either one blank to download an entire user's or subreddit's history
# or fill in both to download a specific users history from a specific subreddit

year = 2022

filter_string = None
if username == "" and subreddit == "":
	print("Fill in either username or subreddit")
	sys.exit(0)
elif username == "" and subreddit != "":
	filter_string = f"subreddit={subreddit}"
elif username != "" and subreddit == "":
	filter_string = f"author={username}"
else:
	filter_string = f"author={username}&subreddit={subreddit}"

url = "https://api.pushshift.io/reddit/{}/search?limit=1000&order=desc&{}&before="

start_time = datetime.strptime("{}-01-01".format(year+1), '%Y-%m-%d')

dictDate = {}

def downloadFromUrl(filename, object_type):
    print(f"Saving {object_type}s to {filename}")
    
    final = []
    
    count = 0
    previous_epoch = int(start_time.timestamp())
    #print(datetime.fromtimestamp(previous_epoch))
    #print(datetime.strptime("{}-01-01".format(year), '%Y-%m-%d'))
    while datetime.fromtimestamp(previous_epoch) >= datetime.strptime("{}-01-01".format(year), '%Y-%m-%d'):
        #print(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))
        if datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d") not in dictDate.keys():
            dictDate[str(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))] = 0
        #print(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))
        new_url = url.format(object_type, filter_string)+str(previous_epoch)
        json_text = requests.get(new_url, headers={'User-Agent': "Post downloader by /u/Watchful1"})
        print(new_url)
        #print(json_text)
        time.sleep(1)  # pushshift has a rate limit, if we send requests too fast it will start returning error messages
        try:
            json_data = json_text.json()
        except json.decoder.JSONDecodeError:
            time.sleep(1)
            continue
        #print(json_data)
        if 'data' not in json_data:
            break
        objects = json_data['data']
        #print(objects)
        if len(objects) == 0:
            break
        
        #print(dictDate[str(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))])
        if dictDate[str(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))] >= 1000:
            previous_epoch = int((datetime.fromtimestamp(previous_epoch) - timedelta(days=1)).timestamp())
            continue
        #print(objects.head())
        for object in objects:
                        
            previous_epoch = object['created_utc'] - 1
            count += 1
            #print(object_type)
            if object_type == 'comment':
                try:
                    if datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d") not in dictDate.keys():
                        dictDate[str(datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d"))] = 0
					
                    temp = {}
                    temp['created_utc'] = datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d")
                    temp['commentID'] = str(object['id'])
                    temp['link'] = ''
                    temp['is_submitter'] = ''
                    temp['author'] = ''
                    temp['author_flair_richtext'] = ''
                    temp['link_id'] = ''
                    temp['parent_id'] = ''
                    temp['score'] = ''
                    temp['body'] = ''
                    
                    if 'permalink' in object.keys():
                        temp['link'] = "https://www.reddit.com{}".format(object['permalink'])
                    if 'is_submitter' in object.keys():
                        temp['is_submitier'] = str(object['is_submitter'])
                    if 'author' in object.keys():
                        temp['author'] = str(object['author'])
                    if 'author_flair_richtext' in object.keys():
                        temp['author_flair_richtext'] = str(object['author_flair_richtext'])
                    if 'link_id' in object.keys():
                        temp['link_id'] = str(object['link_id'])
                    if 'parent_id' in object.keys():
                        temp['parent_id'] = str(object['parent_id'])
                    if 'score' in object.keys():
                        temp['score'] = str(object['score'])
                    if 'body' in object.keys():
                        temp['body'] = object['body']
                        
                    
                    dictDate[datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d")] += 1
                    final.append(temp)

                except Exception as err:
                    s1 = ""
                    if "permalink" in object.keys():
                        s1 = object['permalink']
                    print("Couldn't print comment DataRow: {}".format(count))
                    print(traceback.format_exc())
                    
        print("Saved {} {}s through {}".format(count, object_type, datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d")))

    print(f"Saved {count} {object_type}s")
    with open(filename, 'w') as fp:
        json.dump(final, fp)

#path = r'C:\Users\pscha\OneDrive\Desktop\GA TECH\02 - CLASSES\05 - SPRING 2021\CSE 6242 - Data and Visual Analytics\PROJECT\DATA'
#submissionPath = os.path.join(path, "posts.txt")
#commentPath = os.path.join("comments{}.txt".format(year))

#downloadFromUrl(commentPath, "comment")
downloadFromUrl("comments2022_work.txt", "comment")
