from pathlib import Path
from logging import getLogger
from processor.base.transformer import Transformer
from moviepy.editor import AudioFileClip, VideoFileClip
from tqdm import tqdm
from typing import Dict, Any

logger = getLogger(__name__)


class TemporalCropper(Transformer):
    def __init__(self, 
                 processor_id: str, audio_path: Path, output_path: Path, extension: str, overwrite_existing: bool):
        self.processor_id = processor_id
        self.input_path = audio_path
        self.output_path = output_path
        self.extension = extension
        self.is_overwrite_existing = overwrite_existing

    @property
    def name(self):
        return "TemporalCropper_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if 'CropExtractor_' + self.processor_id  in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data CropExtractor information is not found")
            return {}

        num_videos = len(video_info_dict)
        logger.info("Starting to crop {size} files".format(size=num_videos))
        i = 0

        self.output_path.mkdir(parents=True, exist_ok=True)

        ret = {}
        for (video_id, (video_crop_start, video_crop_end)) in tqdm(video_info_dict.items()):
            i = i + 1
            if i % (num_videos / 10) == 0:
                logger.info("Split progress: {cur}% completed".format(cur=(i / num_videos * 100)))

            try:
                self.split(video_id, video_crop_start, video_crop_end)
                ret[video_id] = {'state': 'Success'}
            except Exception as e:
                logger.warning("Failed to split audio from {vid}, reason: {r}".format(vid=video_id, r=e))
                ret[video_id] = {'state': 'Failed', 'reason': e}

        return ret

    def split(self, video_id: str, crop_start: float = 0, crop_end: float = 0):
        input_file_path = Path(self.input_path, "{vid}.{ext}".format(vid=video_id, ext=self.extension))

        cropped_path = self.output_path / "{vid}.{ext}".format(vid=video_id, ext=self.extension)

        if input_file_path.exists():
            # Audio
            if self.extension == "mp3" and self.should_crop(cropped_path):
                clip = AudioFileClip(str(input_file_path.absolute()))

                if crop_start is not 0 or crop_end is not 0:
                    clip = clip.subclip(crop_start, crop_end)

                if clip.audio:
                    clip.audio.write_audiofile(str(cropped_path.absolute()))

                clip.close()

            elif self.extension == "mp4" and self.should_crop(cropped_path):
                clip = VideoFileClip(str(input_file_path.absolute()))

                if crop_start is not 0 or crop_end is not 0:
                    clip = clip.subclip(crop_start, crop_end)

                if clip:
                    clip.write_videofile(str(cropped_path.absolute()))

                clip.close()
        else:
            # logger.warning('Failed to find file from: %s', input_file_path)
            pass

    def should_crop(self, path: Path):
        return self.is_overwrite_existing or (not path.exists())
