from pathlib import Path
from logging import getLogger
from processor.base.extractor import Extractor, check_valid_partition
from json import load
from processor.util.json_util import json_accessor
from typing import Dict, Any, Tuple, List
from processor.util.dict_util import partition_dict


logger = getLogger(__name__)


class JSONDownloadExtractor(Extractor):
    def __init__(self,
                 processor_id: str,
                 target_list: List[str],
                 part: Tuple[int, int],
                 json_path: Path, list_key: str, url_key: str, id_key: str):
        self.processor_id = processor_id
        self.file_path = json_path
        self.list_key = list_key
        self.url_key = url_key
        self.id_key = id_key
        self.target_list = target_list

        self.part = check_valid_partition(part)

    @property
    def name(self):
        return "JSONDownloadExtractor_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        ret = {}

        try:
            json_file = self.file_path.open()
        except FileNotFoundError:
            logger.error("Unable to find file {file}".format(file=self.file_path))
            return ret

        json_dict = load(json_file)
        try:
            video_info_list = json_accessor(json_dict, self.list_key)
        except KeyError:
            logger.warning("{list} is not found from file {file}".format(list=self.list_key, file=json_file))
            return ret

        if isinstance(video_info_list, dict):
            for (vid, video_info) in video_info_list.items():
                # vid = json_accessor(video_info, self.id_key)
                url = json_accessor(video_info, self.url_key)

                ret[vid] = url
        else:
            for video_info in video_info_list:
                vid = json_accessor(video_info, self.id_key)
                url = json_accessor(video_info, self.url_key)

                ret[vid] = url

        # leave only videos to download
        if self.target_list:
            ret = {video_info: v for (video_info, v) in ret if self.target_list.index(video_info)}

        # partition download list into self.part[1] parts
        if self.part[1] > 1:
            ret = partition_dict(ret, self.part[0], self.part[1])

        return ret
