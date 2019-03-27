from pathlib import Path
from logging import getLogger
from pytube import YouTube, exceptions
from functools import partial
from typing import Dict, Tuple, Any, List
from subprocess import run, DEVNULL, PIPE
from urllib.error import HTTPError
from operator import itemgetter
import platform
import re


logger = getLogger(__name__)


def do_download(download_info: Tuple[Tuple[str, str], int, Path, Dict[str, Any]]) -> Tuple[str, Any]:
    (video_info, i, output_path, download_opt) = download_info

    try:
        video_id = video_info[0]
        url = video_info[1]
    except KeyError:
        logger.warning("Unable to get video id or url from object {data}".format(data=video_info))
        video_id = None
        url = None

    timeout_second = download_opt['timeout']
    if not timeout_second:
        timeout_second = 600

    ret = {'result': 'Not Downloaded'}
    if url:
        try:
            # timeout = Timeout(timeout_second)
            # timeout.start()
            download(url, output_path, "{vid}-progress".format(vid=video_id), download_opt)
            ret['result'] = 'Success'
        except exceptions.VideoUnavailable:
            # logger.warning('Video {vid} from url {url} is now unavailable'.format(vid=video_id, url=url))
            ret['result'] = 'Unavailable'
        # except Timeout:
        #     ret['result'] = 'Timeout after {sec}'.format(sec=timeout_second)
        except Exception as e:
            # logger.warning("Failed to download video {vid} from url {url}, reason: {r}"
            #                .format(vid=video_id, r=e, url=url))

            ret = {'result': 'Failed', 'exception': str(e)}

        progress_path = output_path / "{vid}-progress.{ext}".format(vid=video_id, ext=download_opt['extension'])
        target_path = output_path / "{vid}.{ext}".format(vid=video_id, ext=download_opt['extension'])

        if progress_path.exists():
            if ret['result'] == 'Success':
                progress_path.rename(target_path)
            else:
                progress_path.unlink()
    return video_id, ret


def is_high_res(resolutions_to_exclude: List[str], fmt_streams):
    return not any([fmt_streams.resolution == res for res in resolutions_to_exclude])


def download(url: str, download_path: Path, video_id: str, download_opts: Dict[str, Any]) -> None:
    is_high_res_filter = partial(is_high_res, download_opts['exclude_resolutions'])

    try:
        yt = YouTube(url)
        step = yt.streams
        step2 = step.filter(subtype=download_opts['extension'])

        if not step2:
            step2 = step

        step3 = step2.filter(**download_opts['filter'])

        if not step3:
            step3 = step2

        step4 = step3.filter(custom_filter_functions=[is_high_res_filter])
        if not step4:
            # only high-res video is available
            step4 = step3

        step4.order_by(download_opts['order_by']).desc().first()\
            .download(output_path=str(download_path.absolute()), filename=video_id)
    except (exceptions.RegexMatchError, HTTPError):
        # try another library
        re_starts_with_digit = re.compile(r'^\d')
        re_extension = re.compile(r'^\d+\s+(\w+)')

        if platform.system() == 'Windows':
            executable = './script/processor/downloader/youtube-dl.exe'
        else:
            executable = './script/processor/downloader/youtube-dl'

        result = run([executable, '-F', url], check=True, stdout=PIPE)

        format_list = [line for line in result.stdout.decode('utf-8').split('\n')
                       if re.match(re_starts_with_digit, line)]

        format_list = [line for line in format_list
                       if re.search(re_extension, line).group(1) == download_opts['extension']]

        if 'only_audio' in download_opts['filter'] and download_opts['filter']['only_audio']:
            re_audio_info = re.compile(r'^(?P<id>\d+)\s+(?P<ext>\w+)\s+(audio only)\s+(\w+ \w+)\s+(?P<samplerate>\w+)')
            format_list = [line for line in format_list if 'audio only' in line]
            id_samplerate_list = [(res.group('id'), res.group('samplerate')) for res
                                  in [re.search(re_audio_info, line) for line in format_list]]
            id_samplerate_list.sort(reverse=True, key=itemgetter(1))
            id_str = id_samplerate_list[0][0]
        else:
            format_list = [line for line in format_list if 'video only' in line]
            re_video_info = re.compile(r'^(?P<id>\d+)\s+(?P<ext>\w+)\s+(\w+)\s+(?P<resolution>\w+)')
            format_list = [line for line in format_list if 'audio only' not in line]
            id_resolution_list = [(res.group('id'), res.group('resolution')) for res
                                  in [re.search(re_video_info, line) for line in format_list]]
            id_resolution_list.sort(reverse=True, key=itemgetter(1))
            id_resolution_list = [item for item in id_resolution_list
                                  if not any([item[1] == res for res in download_opts['exclude_resolutions']])]
            id_str = id_resolution_list[0][0]

        run([executable, '-f', id_str, '-o',
            str((download_path / '{vid}.{ext}'.format(vid=video_id, ext=download_opts['extension'])).absolute()),
            '--no-progress', url], check=True, stdout=DEVNULL)
    except Exception as e:
        raise e
