from processor.msr_vtt import MSR_VTT
from processor.sports_1m import Sports1M
from processor.kinetics import Kinetics
from processor.ava import AVA
from logging import getLogger, DEBUG, basicConfig
from util.argparse import parse
from pathlib import Path

basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=DEBUG)
logger = getLogger()

arg_dict = {
    "target_script": {'name': '--TARGET_SCRIPT', 'help': '', 'type': str,}, #AUXILIARY, NOT USED
    'input': {'name': '--input', 'help': '', 'required': True},
    'output': {'name': '--output', 'help': '', 'required': True},
    'part_idx': {'name': '--part_idx', 'help': '', 'type': int, 'default': 0},
    'part_num': {'name': '--part_num', 'help': '', 'type': int, 'default': 1},
    'concurrent_procs': {'name': '--concurrent_procs', 'help': '', 'type': int, 'default': 1},
    'dataset': {'name': '--dataset', 'help': '', 'type': str, 'default': ''},
    'max_resolution': {'name': '--max_resolution', 'type': str, 'default': '480p'},
}

if __name__ == '__main__':

    args = parse(arg_dict)

    input_path = Path(args['input'])
    output_path = Path(args['output'])
    partition_index = args['part_idx']
    partition_num = args['part_num']
    concurrent_procs = args['concurrent_procs']
    dataset = args['dataset']
    max_resolution = args['max_resolution']
    if max_resolution == '720p':
        exclude_resolutions = ['1080p', 'hd']
    elif max_resolution == '480p':
        exclude_resolutions = ['720p', '1080p', 'hd']
    elif max_resolution == '360p':
        exclude_resolutions = ['720p', '1080p', 'hd', '480p']
    elif max_resolution == '240p':
        exclude_resolutions = ['720p', '1080p', 'hd', '480p', '360p']
    elif max_resolution == '120p':
        exclude_resolutions = ['720p', '1080p', 'hd', '480p', '360p', '240p']

    if dataset == 'msr-vtt':

        test_processor = MSR_VTT(input_path / "MSRVTT", output_path / "msrvtt", 
                                 concurrent_procs, (partition_index, partition_num), exclude_resolutions)

        test_processor.process()

    elif dataset == 'sports-1m':
        sports1m_processor = Sports1M(input_path / "sports-1m", output_path / "sports-1m",
                                      concurrent_procs, (partition_index, partition_num), exclude_resolutions)

        sports1m_processor.process()

    elif dataset == 'kinetics':

        kinetics_p = Kinetics(input_path / "Kinetics", output_path / "kinetics",
                              concurrent_procs, (partition_index, partition_num), exclude_resolutions)

        kinetics_p.process()

    elif dataset == 'ava':
        ava_p = AVA(input_path / "AVA", output_path / "ava",
                    concurrent_procs, (partition_index, partition_num), exclude_resolutions)
        ava_p.process()
