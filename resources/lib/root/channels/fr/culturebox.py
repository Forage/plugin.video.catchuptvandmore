# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
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

import ast
import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

'''
Channels:
    * France TV CultureBox
'''

URL_ROOT = 'https://culturebox.francetvinfo.fr'

URL_VIDEOS = URL_ROOT + '/videos/'

SHOW_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s'


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    params['next'] = 'list_shows_1'
    params['mode'] = 'replay'
    params['module_name'] = params.module_name
    params['module_path'] = params.module_path
    return channel_entry(params)

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if 'list_shows_1' in params.next:

        categories_html = utils.get_webcontent(
            URL_VIDEOS)
        categories_soup = bs(categories_html, 'html.parser')
        list_categories = categories_soup.find(
            'nav').find_all('a')

        for category_datas in list_categories:

            if '/videos/' in category_datas.get('href'):
                category_title = category_datas.get_text().encode('utf-8')
                category_url = URL_ROOT + category_datas.get(
                    'href') + '?sort_by=field_live_published_date_value&sort_order=DESC&page=%s'

                shows.append({
                    'label': category_title,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        category_url=category_url,
                        page='0',
                        title=category_title,
                        next='list_videos_1',
                        window_title=category_title
                    )
                })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':

        list_videos_html = utils.get_webcontent(
            params.category_url % (params.page))
        list_videos_soup = bs(list_videos_html, 'html.parser')
        if list_videos_soup.find(
            'ul', class_="live-article-list"):
            list_videos_datas = list_videos_soup.find(
                'ul', class_="live-article-list").find_all(
                    'div', class_="img")

            for video_data in list_videos_datas:

                title = video_data.find(
                    'img').get('alt')
                image = video_data.find(
                    'img').get('data-frz-src')
                duration = 0
                html_video_data = utils.get_webcontent(
                    URL_ROOT + video_data.find('a').get('href'))
                if re.compile(
                    r'videos.francetv.fr\/video\/(.*?)\@').findall(html_video_data):
                    id_diffusion = re.compile(
                        r'videos.francetv.fr\/video\/(.*?)\@').findall(html_video_data)[0]
                else:
                    id_diffusion = ''

                info = {
                    'video': {
                        'title': title,
                        # 'plot': plot,
                        # 'aired': aired,
                        # 'date': date,
                        'duration': duration,
                        # 'year': year,
                    }
                }

                download_video = (
                    common.GETTEXT('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        module_path=params.module_path,
                        module_name=params.module_name,
                        id_diffusion=id_diffusion) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'fanart': image,
                    'thumb': image,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='play_r',
                        id_diffusion=id_diffusion
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                category_url=params.category_url,
                next=params.next,
                page=str(int(params.page) + 1),
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_EPISODE

        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""

    desired_quality = common.PLUGIN.get_setting('quality')

    file_prgm = utils.get_webcontent(SHOW_INFO % (params.id_diffusion))
    json_parser = json.loads(file_prgm)

    url_selected = ''

    if desired_quality == "DIALOG":
        all_datas_videos_quality = []
        all_datas_videos_path = []

        for video in json_parser['videos']:
            if 'hls' in video['format']:
                if video['format'] == 'hls_v5_os':
                    all_datas_videos_quality.append("HD")
                else:
                    all_datas_videos_quality.append("SD")
                all_datas_videos_path.append(
                    (video['url'], video['drm']))

        seleted_item = common.sp.xbmcgui.Dialog().select(
            common.GETTEXT('Choose video quality'),
            all_datas_videos_quality)

        if seleted_item == -1:
            return None

        url_selected = all_datas_videos_path[seleted_item][0]
        drm = all_datas_videos_path[seleted_item][1]

    elif desired_quality == "BEST":
        for video in json_parser['videos']:
            if video['format'] == 'hls_v5_os':
                url_selected = video['url']
                drm = video['drm']
            else:
                url_selected = video['url']
                drm = video['drm']
    else:
        for video in json_parser['videos']:
            if video['format'] == 'm3u8-download':
                url_selected = video['url']
                drm = video['drm']
            else:
                url_selected = video['url']
                drm = video['drm']

    if drm:
        utils.send_notification(
            common.ADDON.get_localized_string(30702))
        return None
    else:
        return url_selected
