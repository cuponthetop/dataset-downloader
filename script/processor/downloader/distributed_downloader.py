from pathlib import Path
from logging import getLogger
from processor.base.downloader import Downloader
from .method import youtube_download
from multiprocessing import Pool
from typing import Dict, Tuple, Any
from itertools import repeat
from tqdm import tqdm


logger = getLogger(__name__)


class DistributedDownloader(Downloader):

    #
    def __init__(self,
                 processor_id: str,
                 download_opt: Dict[str, Any],
                 output_path: Path,
                 pool_size: int = 1,
                 downloader_type: str = 'Youtube',
                 redownload_existing: bool = False):
        self.processor_id = processor_id
        self.download_opt = download_opt
        if 'extension' not in self.download_opt:
            # self.download_opt['extension'] = 'mp4'
            raise Exception('Extension must be specified')
        self.output_path = output_path
        self.redownload_existing = redownload_existing
        self.type = downloader_type

        if pool_size > 1:
            self.pool_size = pool_size
        else:
            self.pool_size = 1

    @property
    def name(self):
        return "DistributedDownloader_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if 'DownloadExtractor_' + self.processor_id in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data DownloadExtractor information is not found")
            return {}

        num_videos = len(video_info_dict)
        chunksize = 1
        if num_videos > 10000:
            # for long lists, document says manually setting chunksize parameter will yield better performance
            chunksize = self.pool_size * 2

        logger.info("Starting to fetch {size} videos".format(size=num_videos))

        if self.output_path.exists() is False:
            self.output_path.mkdir(parents=True, exist_ok=True)

        download_list = list(video_info_dict.items())

        # check for existing files before downloading
        if not self.redownload_existing:
            ext = self.download_opt['extension']
            already_downloaded_files = set([i.stem for i in self.output_path.glob("*.{ext}".format(ext=ext))])

            download_list = [item for item in download_list if item[0] not in already_downloaded_files]

        num_videos = len(download_list)

        do_list = [info for info in
                   zip(download_list, range(0, num_videos),
                       repeat(self.output_path),
                       repeat(self.download_opt)
                       )]

        download_func = self.get_download_func()

        if self.pool_size > 1:
            with Pool(self.pool_size) as pool:
                ret = list(tqdm(pool.imap(download_func, do_list, chunksize=1), total=num_videos))
        else:
            ret = list(tqdm(map(download_func, do_list), total=num_videos))

        logger.info('Finished downloading videos into {out}'.format(out=self.output_path))

        return dict(ret)

    def get_download_func(self):
        if self.type == 'Youtube':
            return youtube_download
