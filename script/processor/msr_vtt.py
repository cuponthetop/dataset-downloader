from processor.base.dataset import Dataset
# downloader
from processor.downloader.youtube_video_downloader import YouTubeVideoDownloader
from processor.downloader.youtube_audio_downloader import YouTubeAudioDownloader
# cropper
from processor.transformer.temporal_cropper import TemporalCropper
from processor.transformer.video_audio_splitter import VideoAudioSplitter
from processor.transformer.video_framer import VideoFramer

# extractor
from processor.extractor.json_crop_extractor import JSONCropExtractor
from processor.extractor.json_download_extractor import JSONDownloadExtractor

# writer
from processor.writer.result_writer import ResultWriter

from pathlib import Path
from typing import Tuple, List


class MSR_VTT(Dataset):
    TEST_FILENAME = "test_videodatainfo_nosen_2017.json"
    TRAIN_FILENAME = "videodatainfo_2017.json"

    def __init__(self, input_path: Path, output_path: Path, num_concurrent_processes: int, partition: Tuple[int, int],
                 exclude_resolutions: List[str]):
        super(MSR_VTT, self).__init__()
        raw_path = input_path
        intermediate_path = output_path

        # Train Set
        self.append_extractor(JSONDownloadExtractor("train", [], partition,
                                                    raw_path / self.TRAIN_FILENAME,
                                                    "videos", "url", "id"))
        # self.append_extractor(JSONCropExtractor("train", [], partition,
        #                                         raw_path / self.TRAIN_FILENAME,
        #                                         "videos", "id", "start time", "end time"))
        #
        self.append_downloader(YouTubeVideoDownloader(intermediate_path / "train" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))

        # self.append_transformer(TemporalCropper("train", intermediate_path / "train" / "full",
        #                                         intermediate_path / "train" / "cropped",
        #                                         "mp4", False))
        #

        # Test Set
        # self.append_extractor(JSONDownloadExtractor("test", [], partition,
        #                                             raw_path / self.TEST_FILENAME,
        #                                             "videos", "url", "id"))
        # self.append_extractor(JSONCropExtractor("test", [], partition,
        #                                         raw_path / self.TEST_FILENAME,
        #                                         "videos", "id", "start time", "end time"))

        # self.append_downloader(YouTubeVideoDownloader("test", intermediate_path / "test" / "full",
        #                                               num_concurrent_processes, False, exclude_resolutions))
        # self.append_transformer(TemporalCropper("test", intermediate_path / "test" / "full",
        #                                         intermediate_path / "test" / "cropped",
        #                                         "mp4", False))

        # self.append_downloader(YouTubeAudioDownloader("test", result_path / "train" / "audio",
        #                                                num_concurrent_processes, False))
        #
        # self.append_transformer(VideoAudioSplitter("VideoDownloader_",
        #                                            intermediate_path / "train" / "full",
        #                                            intermediate_path / "train" / "audio",
        #                                            "mp4", "mp3"))
        #
        # self.append_transformer(VideoFramer("Cropper",
        #                                     intermediate_path / "train" / "full",
        #                                     result_path / "train" / "frames",
        #                                     "mp4", "png", target_fps))
        #
        self.append_writers(ResultWriter("overall", partition[0], intermediate_path / "result", True))
