import tarfile
from pathlib import Path
from processor.base.transformer import Transformer
from typing import Dict, Any
from logging import getLogger
import requests
import tensorflow as tf
import tensorflow_hub as hub


logger = getLogger(__name__)


# output of 4096-dimensional fc6 layer from AlexNet, VGG-16 and VGG-19 and
# pool5/7x7s1 layer of GoogleNet pre-trained on ImageNet dataset.
# C3D pre-trained on Sports-1M video dataset


class TFFeatureExtractor(Transformer):
    MODELS = {
        'Inception V1': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/inception_v1/feature_vector/1',
        },
        'Inception V2': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/inception_v2/feature_vector/1',
        },
        'Inception V3': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/inception_v3/feature_vector/1',
        },
        'Inception V4': {
            'type': 'tf_model',
            'filename': 'inception_v4_2016_09_09',
            'url': 'http://download.tensorflow.org/models/inception_v4_2016_09_09.tar.gz',
        },
        'Inception-ResNet-v2': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/inception_resnet_v2/feature_vector/1',
        },
        'ResNet V1 50': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v1_50/feature_vector/1',
        },
        'ResNet V1 101': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v1_101/feature_vector/1',
        },
        'ResNet V1 152': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v1_152/feature_vector/1',
        },
        'ResNet V2 50': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v2_50/feature_vector/1',
        },
        'ResNet V2 101': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v2_101/feature_vector/1',
        },
        'ResNet V2 152': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/resnet_v2_152/feature_vector/1',
        },
        'MobileNet V2 140 224': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/2',
        },
        'VGG 16': {
            'type': 'tf_model',
            'filename': 'vgg_16_2016_08_28',
            'url': 'http://download.tensorflow.org/models/vgg_16_2016_08_28.tar.gz',
        },
        'VGG 19': {
            'type': 'tf_model',
            'filename': 'vgg_19_2016_08_28',
            'url': 'http://download.tensorflow.org/models/vgg_19_2016_08_28.tar.gz',
        },
        'ELMO V1': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/elmo/1',
        },
        'ELMO V2': {
            'type': 'hub',
            'url': 'https://tfhub.dev/google/elmo/2',
        },
        'I3D Kinetics 400': {
            'type': 'hub',
            'url': 'https://tfhub.dev/deepmind/i3d-kinetics-400/1',
        },
        'I3D Kinetics 600': {
            'type': 'hub',
            'url': 'https://tfhub.dev/deepmind/i3d-kinetics-600/1',
        },
    }

    def __init__(self, model: str, input_path: Path, output_path: Path):
        try:
            self.model = model
            model_info = self.MODELS[model]
            self.model_url = model_info['url']
            self.type = model_info['type']
            if self.type == 'hub':
                pass
            elif self.type == 'tf_model':
                self.model_filename = model_info['filename']
                self.model_tensor_name = model_info['tensor_name']
                self.model_stop_gradient = model_info['stop_gradient']
        except KeyError:
            raise Exception('Requested Model {model_name} not found'.format(model_name=model))

        self.output_path = output_path
        self.input_path = input_path

        self.model_dir_path = self.output_path / 'model'
        self.model_path = self.model_dir_path / '{model}.tar.gz'.format(model=self.model_filename)
        self.checkpoint_path = self.model_dir_path / '{model}.ckpt'.format(model=self.model_filename)

    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        ret = {}
        with tf.Session() as sess:
            if self.type == 'hub':
                model = hub.Module(self.model_url)
            elif self.type == 'tf_model':
                tf.saved_model.loader.load(sess, self.checkpoint_path)
                graph = tf.get_default_graph()
                model = graph.get_tensor_by_name(self.model_tensor_name)
                if self.model_stop_gradient:
                    model = tf.stop_gradient(model)

            ## iterate

        return ret

    def download_model(self):
        if not self.model_dir_path.exists():
            self.model_dir_path.mkdir(parents=True)

        if not self.model_path.exists() and not self.checkpoint_path.exists():
            try:
                open('{model}.tar.gz'.format(model=self.model), 'wb')\
                    .write(requests.get(self.model_url, allow_redirects=True).content)
            except Exception as e:
                logger.warning('Failed to download pre-trained model {model}, reason: {e}'
                               .format(model=self.model, e=e))
                raise e

    def unzip_model(self):
        if self.model_path.exists() and not self.checkpoint_path.exists():
            with tarfile.open(self.model_path, "r:gz") as tar:
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar)
                tar.close()
