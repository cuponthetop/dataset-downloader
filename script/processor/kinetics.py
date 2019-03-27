from processor.base.dataset import Dataset
# downloader
from processor.downloader.youtube_video_downloader import YouTubeVideoDownloader
from processor.downloader.youtube_audio_downloader import YouTubeAudioDownloader
# cropper
from processor.transformer.temporal_cropper import TemporalCropper

# extractor
from processor.extractor.json_crop_extractor import JSONCropExtractor
from processor.extractor.json_download_extractor import JSONDownloadExtractor

# writer
from processor.writer.result_writer import ResultWriter

from pathlib import Path
from typing import Tuple, List


class Kinetics(Dataset):
    TEST_FILENAME = "kinetics_600_test.json"
    TRAIN_FILENAME = "kinetics_train.json"
    VAL_FILENAME = "kinetics_val.json"
    HOLD_OUT_FILENAME = "kinetics_600_holdout_test.json"

    def __init__(self, input_path: Path, output_path: Path, num_concurrent_processes, partition: Tuple[int, int],
                 exclude_resolutions: List[str]):
        super(Kinetics, self).__init__()
        raw_path = input_path
        intermediate_path = output_path

        VIDEO_ACCESSOR = None
        URL_ACCESSOR = "url"
        ID_ACCESSOR = None

        START_TIME_ACCESSOR = "annotations.segment.0"
        END_TIME_ACCESSOR = "annotations.segment.1"


        # Train Set
        self.append_extractor(JSONDownloadExtractor("train", [], partition,
                                                    raw_path / self.TRAIN_FILENAME,
                                                    VIDEO_ACCESSOR, URL_ACCESSOR, ID_ACCESSOR))
        self.append_extractor(JSONCropExtractor("train", [], partition,
                                                raw_path / self.TRAIN_FILENAME,
                                                VIDEO_ACCESSOR, ID_ACCESSOR, START_TIME_ACCESSOR, END_TIME_ACCESSOR))

        self.append_downloader(YouTubeVideoDownloader("train", intermediate_path / "train" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))

        self.append_transformer(TemporalCropper("train", intermediate_path / "train" / "full",
                                                intermediate_path / "train" / "cropped",
                                                "mp4", False))

        # Test Set
        self.append_extractor(JSONDownloadExtractor('test', [], partition,
                                                    raw_path / self.TEST_FILENAME,
                                                    VIDEO_ACCESSOR, URL_ACCESSOR, ID_ACCESSOR))
        self.append_extractor(JSONCropExtractor('test', [], partition,
                                                raw_path / self.TEST_FILENAME,
                                                VIDEO_ACCESSOR, ID_ACCESSOR, START_TIME_ACCESSOR, END_TIME_ACCESSOR))

        self.append_downloader(YouTubeVideoDownloader('test', intermediate_path / "test" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))
        self.append_transformer(TemporalCropper('test', intermediate_path / "test" / "full",
                                                intermediate_path / "test" / "cropped",
                                                "mp4", False))

        # Validation Set
        self.append_extractor(JSONDownloadExtractor('validation', [], partition,
                                                    raw_path / self.VAL_FILENAME,
                                                    VIDEO_ACCESSOR, URL_ACCESSOR, ID_ACCESSOR))
        self.append_extractor(JSONCropExtractor('validation', [], partition,
                                                raw_path / self.VAL_FILENAME,
                                                VIDEO_ACCESSOR, ID_ACCESSOR, START_TIME_ACCESSOR, END_TIME_ACCESSOR))

        self.append_downloader(YouTubeVideoDownloader('validation', intermediate_path / "test" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))
        self.append_transformer(TemporalCropper('validation', intermediate_path / "test" / "full",
                                                intermediate_path / "test" / "cropped",
                                                "mp4", False))

        # Holdout Set
        self.append_extractor(JSONDownloadExtractor('holdout', [], partition,
                                                    raw_path / self.HOLD_OUT_FILENAME,
                                                    VIDEO_ACCESSOR, URL_ACCESSOR, ID_ACCESSOR))
        self.append_extractor(JSONCropExtractor('holdout', [], partition,
                                                raw_path / self.HOLD_OUT_FILENAME,
                                                VIDEO_ACCESSOR, ID_ACCESSOR, START_TIME_ACCESSOR, END_TIME_ACCESSOR))

        self.append_downloader(YouTubeVideoDownloader('holdout', intermediate_path / "test" / "full",
                                                      num_concurrent_processes, False, exclude_resolutions))
        self.append_transformer(TemporalCropper('holdout', intermediate_path / "test" / "full",
                                                intermediate_path / "test" / "cropped",
                                                "mp4", False))

        # self.append_downloader(YouTubeAudioDownloader(result_path / "train" / "audio", 10, False))
        #
        # self.append_transformer(VideoAudioSplitter("VideoDownloader_",
        #                                            intermediate_path / "train" / "full",
        #                                            intermediate_path / "train" / "audio",
        #                                            "mp4", "mp3"))
        #

        self.append_writers(ResultWriter("overall", partition[0], intermediate_path / "result", True))
