from pathlib import Path
from logging import getLogger
from .distributed_downloader import DistributedDownloader
from typing import Dict, Tuple, Any, List


logger = getLogger(__name__)


class YouTubeVideoDownloader(DistributedDownloader):

    #
    def __init__(self, 
                 processor_id: str, output_path: Path,
                 pool_size: int = 1,
                 redownload_existing: bool = False,
                 exclude_resolution_list: List[str] = None,
                 extension: str = 'webm'):
        super().__init__(processor_id, {
            'extension': extension,
            'filter': {'mime_type': 'video/{ext}'.format(ext=extension)},
            'exclude_resolutions': exclude_resolution_list,
            'order_by': 'resolution',
            'timeout': 1, #900,
        }, output_path, pool_size, "Youtube", redownload_existing)

    @property
    def name(self):
        return "YouTubeVideoDownloader_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return super().process(data)
