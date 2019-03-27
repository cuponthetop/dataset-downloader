from pathlib import Path
from logging import getLogger
from processor.base.transformer import Transformer
from moviepy.editor import VideoFileClip
from typing import Dict, Any

logger = getLogger(__name__)


class VideoAudioSplitter(Transformer):
    # source_of_targets - 어떤 변환자의 결과를 바탕으로 비디오를 프레임으로 나눌 것인가?
    #                     ex) VideoDownloader, Cropper, Splitter, DownloadExtractor, etc.
    # src_extension - 입력 비디오 파일의 확장자
    # dest_extension - 출력 오디오 파일의 확장자
    def __init__(self,
                 processor_id: str, source_of_targets: str,
                 video_path: Path, output_path: Path,
                 src_extension: str, dest_extension: str):
        self.processor_id = processor_id
        self.video_path = video_path
        self.output_path = output_path
        self.src_extension = src_extension,
        self.dest_extension = dest_extension
        self.data_key = source_of_targets

    @property
    def name(self):
        return "VideoAudioSplitter_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if self.data_key in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data CropExtractor information is not found")
            return {}

        num_videos = len(video_info_dict)

        logger.info("Starting to split audio from {size} videos".format(size=num_videos))
        i = 0

        self.output_path.mkdir(parents=True, exist_ok=True)

        ret = {}
        for (video_id, _) in video_info_dict:
            i = i + 1
            if i % (num_videos / 10) == 0:
                logger.info("Split progress: {cur}% completed".format(cur=(i / num_videos)))
            try:
                self.split(video_id)
                ret[video_id] = {'state': 'Success'}
            except Exception as e:
                logger.warning("Failed to split audio from {vid}, reason: {r}".format(vid=video_id, r=e))
                ret[video_id] = {'state': 'Failed', 'reason': e}

        return ret

    def split(self, video_id: str):
        video_path = Path(self.video_path, "{vid}.{ext}".format(vid=video_id, ext=self.src_extension))
        if video_path.exists():
            clip = VideoFileClip(str(video_path.absolute()))

            if clip.audio:
                audio_path = self.output_path / "{vid}.{ext}".format(vid=video_id, ext=self.dest_extension)
                clip.audio.write_audiofile(str(audio_path.absolute()))

            clip.close()
        else:
            logger.warning('Failed to find video from: %s', video_path)
