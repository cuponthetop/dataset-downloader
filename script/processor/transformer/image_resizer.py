from pathlib import Path
from logging import getLogger
from processor.base.transformer import Transformer
from PIL import Image
from typing import Dict, Any, Union, List

logger = getLogger(__name__)


class ImageResizer(Transformer):
    # target_size -
    def __init__(self,
                 processor_id: str, video_path: Path, output_path: Path,
                 target_size_anchor_axis: int, dest_extension: str,
                 target_anchor_axis: Union[str, None] = None
                 ):
        self.processor_id = processor_id
        self.video_path = video_path
        self.output_path = output_path
        self.target_size_anchor_axis = target_size_anchor_axis
        self.dest_extension = dest_extension
        self.target_anchor_axis = target_anchor_axis

    @property
    def name(self):
        return "ImageResizer_" + self.processor_id

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            extractor_data = {k: v for (k, v) in data.items() if 'Framer_' + self.processor_id in k}
            (extractor_name, video_info_dict) = next(iter(extractor_data.items()))
        except KeyError:
            logger.warning("Required data VideoFramer information is not found")
            return {}

        num_videos = len(video_info_dict)

        logger.info("Starting to resize {size} video frames to images with {x} short side"
                    .format(size=num_videos, x=self.target_size_anchor_axis))

        i = 0

        ret = {}
        for (video_id, result_dict) in video_info_dict:
            i = i + 1
            if i % (num_videos / 10) == 0:
                logger.info("Resizing progress: {cur}% completed".format(cur=(i / num_videos)))

            try:
                resized_frames = self.resize(video_id, result_dict)
                ret[video_id] = {'state': 'Success', 'frame_files': resized_frames}
            except Exception as e:
                logger.warning("Failed to resize video {vid}, reason: {r}".format(vid=video_id, r=e))
                ret[video_id] = {'state': 'Failed', 'reason': e}

        return ret

    def resize(self, video_id: str, result_dict: Dict[str, Union[str, List[str]]]) -> List[str]:
        ret = []
        if result_dict['state'] and result_dict == 'Success':

            output_path = self.output_path / "{vid}".format(vid=video_id)
            output_path.mkdir(parents=True, exist_ok=True)

            i = 0
            for image_path in result_dict['frame_files']:
                i = i + 1
                try:

                    image = Image.open(image_path)
                    (width, height) = image.size

                    if self.target_anchor_axis:
                        shorter_side = min(width, height)
                        resize_ratio = self.target_size_anchor_axis / shorter_side
                    else:
                        if self.target_anchor_axis == 'width':
                            resize_ratio = self.target_size_anchor_axis / width
                        elif self.target_anchor_axis == 'height':
                            resize_ratio = self.target_size_anchor_axis / height
                        else:
                            resize_ratio = 1.0
                            logger.warning('Unsupported target anchor axis {axis}'.format(axis=self.target_anchor_axis))

                    if resize_ratio > 1.0:
                        logger.info('Upsampling image {i} by {ratio}'.format(i=i, ratio=resize_ratio))

                    resized = image.resize((resize_ratio * width, resize_ratio * height))

                    file_path = output_path / "{i}.{ext}".format(i=i, ext=self.dest_extension)
                    resized.save(str(file_path.absolute()))
                    ret.append(str(file_path.absolute()))

                    resized.close()
                    image.close()
                except Exception as e:
                    logger.warning('Failed to resize image from: %s, %s exception occurred', image_path, e)

        return ret
