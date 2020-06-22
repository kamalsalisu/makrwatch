import json
from collections import OrderedDict
import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render
import redis

from django.urls import reverse

from makr import tasks
from makrwatch.settings import YOUTUBE_SEARCH_URL, YOUTUBE_VIDEO_URL, YOUTUBE_API_KEY

redis = redis.Redis()


def index(request):
    if request.method == 'POST':
        keyword = request.POST['search']
        if not redis.get(keyword):
            # Here, we are only getting first 50 results
            search_params = {
                'key': YOUTUBE_API_KEY,
                'part': 'snippet',
                'q': keyword,
                'maxResults': '50',
                'order': 'date',
                'type': 'video'
            }
            search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            json_data = search_response.json()
            next_token = json_data.get("nextPageToken")
            if next_token:
                tasks.fetch_all(keyword,
                                next_token)  # This task runs in the background to fetch the remaining 150 results
            videos_list = []
            video_data = OrderedDict()
            for r in search_response.json()['items']:
                videos_list.append(r['id']['videoId'])  # gather all video ids to use for next query
                video_data[r['id']['videoId']] = r['snippet']  # save video data from search endpoint
            videos_params = {
                'key': YOUTUBE_API_KEY,
                'part': 'statistics',
                'id': ','.join(videos_list),
            }
            videos_response = requests.get(YOUTUBE_VIDEO_URL, params=videos_params)  # second query to get video views
            results = videos_response.json()['items']
            videos = []
            for r in results:
                data = video_data.get(r['id'])
                data['views'] = r['statistics']['viewCount']  # append views to video data
                data['url'] = f"https://www.youtube.com/watch?v={r['id']}"  # generate url
                videos.append(data)
            new_cache = json.dumps(videos)
            redis.setex(keyword, 600, new_cache)  # cache the result
            context = {
                'videos': videos,
                'keyword': keyword,
                'show_all': False
            }
            return render(request, "makr/result.html", context)

        cached = redis.get(keyword)
        cached_videos = json.loads(cached)
        context = {
            'videos': cached_videos,
            'keyword': keyword,
            'show_all': True
        }
        return render(request, "makr/result.html", context)
    return render(request, "makr/index.html")


def result(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        if redis.get(keyword):
            cached = redis.get(keyword)
            cached_videos = json.loads(cached)
            context = {
                'videos': cached_videos,
                'keyword': keyword,
                'show_all': True,
                'scroll': True
            }
            return render(request, "makr/result.html", context)
        return HttpResponseRedirect(reverse('makr:index'))
    return HttpResponseRedirect(reverse('makr:index'))
