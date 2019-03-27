from pathlib import Path
from logging import getLogger
from processor.base.extractor import Extractor, check_valid_partition
from typing import Dict, Any, Tuple, List
from processor.util.dict_util import partition_dict


logger = getLogger(__name__)


class TextDownloadExtractor(Extractor):
    def __init__(self,
                 processor_id: str,
                 target_list: List[str],
                 part: Tuple[int, int],
                 text_path: Path, url_loc: int, delimiter: str = ' '):
        self.processor_id = processor_id
        self.file_path = text_path
        self.url_loc = url_loc
        self.delimiter = delimiter
        self.target_list = target_list

        self.part = check_valid_partition(part)

    @property
    def name(self):
        return "TextDownloadExtractor_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        ret = {}

        try:
            json_file = self.file_path.open()
        except FileNotFoundError:
            logger.error("Unable to find file {file}".format(file=self.file_path))
            return ret

        lines = json_file.readlines()

        for vid, video_info in enumerate(lines):
            try:
                url = video_info.split(self.delimiter)[self.url_loc]

                ret['{v}'.format(v=vid)] = url
            except KeyError:
                logger.error("Unable to find url at {loc} from line: {line}".format(loc=self.url_loc, line=video_info))

        # leave only videos to download
        if self.target_list:
            ret = {video_info: v for (video_info, v) in ret if self.target_list.index(video_info)}

        # partition download list into self.part[1] parts
        if self.part[1] > 1:
            ret = partition_dict(ret, self.part[0], self.part[1])

        return ret
