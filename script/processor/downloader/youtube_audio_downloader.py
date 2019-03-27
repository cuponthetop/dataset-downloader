from pathlib import Path
from logging import getLogger#, DEBUG
from .distributed_downloader import DistributedDownloader
from typing import Dict, Any


logger = getLogger(__name__)


class YouTubeAudioDownloader(DistributedDownloader):
    def __init__(self, 
                 processor_id: str, output_path: Path, pool_size: int = 1, redownload_existing: bool = False):
        super().__init__(processor_id, {
            'extension': 'mp3',
            'filter': {'only_audio': True},
            'order_by': 'abr',
            'timeout': 300,
        }, output_path, pool_size, "Youtube", redownload_existing)

    @property
    def name(self):
        return "YouTubeAudioDownloader_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return super().process(data)
