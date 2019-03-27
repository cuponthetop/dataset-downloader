from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Tuple


class Extractor(metaclass=ABCMeta):

    @abstractmethod
    def process(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        pass

    @property
    def name(self) -> str:
        return 'BaseExtractor'


def check_valid_partition(part: Tuple[int, int]) -> Tuple[int, int]:
    if part[1] > 1 and part[0] >= 0 and (part[0] <= part[1]):
        return part
    else:
        return 0, 1
