from abc import ABCMeta, abstractmethod
from typing import Dict, Any


class Writer(metaclass=ABCMeta):

    @abstractmethod
    def process(self, data: Dict[str, Dict[str, Any]], filename: str) -> Dict[str, Any]:
        pass

    @property
    def name(self) -> str:
        return 'BaseWriter'
