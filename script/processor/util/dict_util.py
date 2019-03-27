import itertools
from typing import Dict, Any


def partition_dict(dict_in: Dict[Any, Any], partition_index: int, num_partition: int):
    n = len(dict_in) // num_partition
    it = iter(sorted(dict_in.items()))

    ret = dict(itertools.islice(it, partition_index * n, partition_index * n + n))

    return ret
