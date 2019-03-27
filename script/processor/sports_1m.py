from typing import Tuple, List
from processor.base.dataset import Dataset
# downloader
from processor.downloader.youtube_video_downloader import YouTubeVideoDownloader
# extractor
from processor.extractor.text_download_extractor import TextDownloadExtractor
# writer
from processor.writer.result_writer import ResultWriter
from pathlib import Path


class Sports1M(Dataset):
    TEST_FILENAME = "test_partition.txt"
    TRAIN_FILENAME = "train_partition.txt"

    def __init__(self, input_path: Path, output_path: Path, num_concurrent_processes: int, partition: Tuple[int, int],
                 exclude_resolutions: List[str]):
        super(Sports1M, self).__init__()
        raw_path = input_path
        intermediate_path = output_path

        # Train
        self.append_extractor(TextDownloadExtractor("train", [], partition, raw_path / self.TRAIN_FILENAME, 0, ' '))

        self.append_downloader(YouTubeVideoDownloader("train", intermediate_path / "train" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))

        # Test
        self.append_extractor(TextDownloadExtractor("test", [], partition, raw_path / self.TEST_FILENAME, 0, ' '))

        self.append_downloader(YouTubeVideoDownloader("test", intermediate_path / "test" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))

        self.append_writers(ResultWriter("overall", partition[0], intermediate_path / "result", True))

