from pathlib import Path
from logging import getLogger
from processor.base.transformer import Transformer
from moviepy.editor import VideoFileClip
from PIL import Image
from typing import Dict, Any
from numpy import lcm, gcd

logger = getLogger(__name__)


class VideoFramer(Transformer):
    # source_of_targets - 어떤 변환자의 결과를 바탕으로 비디오를 프레임으로 나눌 것인가?
    #                     ex) VideoDownloader, Cropper, Splitter, DownloadExtractor, etc.
    # src_extension - 입력 비디오 파일의 확장자
    # dest_extension - 출력 이미지 파일의 확장자
    # target_fps - 프레임 샘플링 목표 FPS
    def __init__(self, 
                 processor_id: str,
                 source_of_targets: str,
                 video_path: Path, output_path: Path,
                 src_extension: str, dest_extension: str, target_fps: float):
        self.processor_id = processor_id
        self.video_path = video_path
        self.output_path = output_path
        self.src_extension = src_extension,
        self.dest_extension = dest_extension
        self.data_key = source_of_targets
        self.target_fps = target_fps

    @property
    def name(self):
        return "VideoFramer_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if self.data_key in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data CropExtractor information is not found")
            return {}

        num_videos = len(video_info_dict)

        logger.info("Starting to split {size} videos into frames".format(size=num_videos))
        i = 0

        ret = {}
        for (video_id, _) in video_info_dict:
            i = i + 1
            if i % (num_videos / 10) == 0:
                logger.info("Splitting progress: {cur}% completed".format(cur=(i / num_videos)))

            try:
                frame_files = self.split_frame(video_id)
                ret[video_id] = {'state': 'Success', 'frame_files': frame_files}
            except Exception as e:
                logger.warning("Failed to frame video {vid}, reason: {r}".format(vid=video_id, r=e))
                ret[video_id] = {'state': 'Failed', 'reason': e}

        return ret

    def split_frame(self, video_id: str):
        video_path = Path(self.video_path, "{vid}.mp4".format(vid=video_id))

        output_path = self.output_path / "{vid}".format(vid=video_id)
        output_path.mkdir(parents=True, exist_ok=True)

        ret = []
        if video_path.exists():
            clip = VideoFileClip(str(video_path.absolute()))

            # assuming original_fps is integer...
            original_fps = clip.fps
            # cannot super-sample
            subsample = original_fps > self.target_fps

            large_num = 1000000000000
            decimal_point = (int((self.target_fps % 1) * large_num) % large_num) / large_num
            integer_value = int(self.target_fps // 1)
            denominator = 10 ** len(str(decimal_point).split('.')[1])
            numerator = decimal_point * denominator
            den_num_gcd = gcd(denominator, numerator)
            denominator, numerator = denominator // den_num_gcd, numerator // den_num_gcd

            original_frame_per_denom_sec = original_fps * denominator
            target_frame_per_denom_sec = numerator + denominator * integer_value
            # !! LOSING REMAINDER
            sampling_rate = int(original_frame_per_denom_sec // target_frame_per_denom_sec)

            i = 0
            for frame in clip.iter_frames():
                if not subsample or (i % sampling_rate) == 0:
                    im = Image.fromarray(frame)
                    file_path = output_path / "{i}.{ext}".format(i=i, ext=self.dest_extension)
                    im.save(str(file_path.absolute()))
                    ret.append(str(file_path.absolute()))
                i = i + 1

            clip.close()
        else:
            logger.warning('Failed to find video from: %s', video_path)

        return ret
