from pathlib import Path
from logging import getLogger
from processor.base.transformer import Transformer
from PIL import Image
from typing import Dict, Any, Union, List
from random import randint

logger = getLogger(__name__)


class ImageCropper(Transformer):
    # crop_size -
    # crop_strategy - "center", "random"
    def __init__(self,
                 processor_id: str, video_path: Path, output_path: Path,
                 crop_size: (int, int), dest_extension: str,
                 crop_strategy: str, crop_num: int):
        self.processor_id = processor_id
        self.video_path = video_path
        self.output_path = output_path
        self.target_crop_size = crop_size
        self.crop_strategy = crop_strategy
        self.dest_extension = dest_extension
        self.num_crop = crop_num

    @property
    def name(self):
        return "ImageCropper_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if 'Framer_' + self.processor_id in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data VideoFramer information is not found")
            return {}

        num_videos = len(video_info_dict)

        logger.info("Starting to crop {size} video frames into {x} x {y} image ({num_crop})"
                    .format(size=num_videos, x=self.target_crop_size[0], y=self.target_crop_size[1],
                            num_crop=self.num_crop))

        i = 0

        ret = {}
        for (video_id, result_dict) in video_info_dict:
            i = i + 1
            if i % (num_videos / 10) == 0:
                logger.info("Resizing progress: {cur}% completed".format(cur=(i / num_videos)))

            try:
                cropped_frames = self.crop(video_id, result_dict)
                ret[video_id] = {'state': 'Success', 'frame_files': cropped_frames}
            except Exception as e:
                logger.warning("Failed to resize video {vid}, reason: {r}".format(vid=video_id, r=e))
                ret[video_id] = {'state': 'Failed', 'reason': e}

        return ret

    def crop(self, video_id: str, result_dict: Dict[str, Union[str, List[str]]]) -> List[str]:
        ret = []
        if result_dict['state'] and result_dict == 'Success':

            output_path = self.output_path / "{vid}".format(vid=video_id)
            output_path.mkdir(parents=True, exist_ok=True)

            i = 0
            for image_path in result_dict['frame_files']:
                i = i + 1
                try:
                    image = Image.open(image_path)
                    for j in range(0, self.num_crop):
                        (width, height) = image.size

                        crop_rect = calc_crop_rect(self.crop_strategy, width, height)
                        cropped = image.crop(crop_rect)

                        file_path = output_path / "{i}_{j}.{ext}".format(i=i, j=j, ext=self.dest_extension)
                        cropped.save(str(file_path.absolute()))
                        ret.append(str(file_path.absolute()))
                        cropped.close()
                        image.close()
                except Exception as e:
                    logger.warning('Failed to resize image from: %s, %s exception occurred', image_path, e)

        return ret


def calc_crop_rect(strategy: str, original_size: (int, int), target_size: (int, int)) -> (int, int, int, int):
    (o_w, o_h) = original_size
    (t_w, t_h) = target_size

    ret = (0, 0, 0, 0)

    if (o_w < t_w) or (o_h < t_h):
        raise ValueError('Original Image is smaller than desired cropped image size')

    if strategy == "center":
        ret = ((o_w - t_w) // 2, (o_h - t_h) // 2, (o_w + t_w) // 2, (o_h + t_h) // 2)
    elif strategy == "random":
        left = randint(0, o_w - t_w)
        upper = randint(0, o_h - t_h)

        ret = (left, upper, left + t_w, upper + t_h)

    return ret

