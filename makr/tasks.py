import json
from collections import OrderedDict
import redis as redis
import requests
from huey.contrib.djhuey import task

from makrwatch.settings import YOUTUBE_SEARCH_URL, YOUTUBE_VIDEO_URL, YOUTUBE_API_KEY

redis = redis.Redis()


@task()
def fetch_all(keyword, next_token):
    count = 3  # For the remaining 150 videos ( 3 * 50 )
    videos = []
    while next_token and count is not 0:
        search_params = {
            'key': YOUTUBE_API_KEY,
            'part': 'snippet',
            'q': keyword,
            'maxResults': '50',
            'order': 'date',
            'type': 'video',
            'pageToken': next_token
        }
        search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
        json_data = search_response.json()
        next_token = json_data.get("nextPageToken")
        videos_list = []
        video_data = OrderedDict()
        for r in search_response.json()['items']:
            videos_list.append(r['id']['videoId'])  # gather all video ids to use for next query
            video_data[r['id']['videoId']] = r['snippet']  # save video data from search endpoint
        videos_params = {
            'key': 'AIzaSyCBa7p6H8fzlULejUu_Dxh4g8gP6bhL2IM',
            'part': 'statistics',
            'id': ','.join(videos_list),
        }
        videos_response = requests.get(YOUTUBE_VIDEO_URL, params=videos_params)  # second query to get video views
        results = videos_response.json()['items']
        for result in results:
            data = video_data.get(result['id'])
            data['views'] = result['statistics']['viewCount']  # append views to video data
            data['url'] = f"https://www.youtube.com/watch?v={result['id']}"  # generate url
            videos.append(data)
        count -= 1
    cached = redis.get(keyword)  # fetch cached videos from redis
    cached_videos = json.loads(cached)
    cached_videos.extend(videos)  # append new videos to cached
    all_videos = json.dumps(cached_videos)
    redis.setex(keyword, 600, all_videos)  # set cache to all videos
