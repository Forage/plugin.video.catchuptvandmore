# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Add Replay


URL_ROOT = 'http://teleticino.ch'

# Live
URL_LIVE = URL_ROOT + '/diretta'


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_videos_1"
        return list_videos(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)

def get_video_url(params):
    """Get video URL and start video player"""
    live_html = utils.get_webcontent(URL_LIVE)
    list_live = re.compile(
        r'file":  "(.*?)"').findall(live_html)
    stream_url = ''
    for stream in list_live:
        if 'm3u8' in stream:
            stream_url = stream
    return stream_url