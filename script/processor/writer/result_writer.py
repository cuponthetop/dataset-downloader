from pathlib import Path
from logging import getLogger
from processor.base.writer import Writer
from typing import Dict, Any
import time
import csv

logger = getLogger(__name__)


class ResultWriter(Writer):
    def __init__(self,
                 processor_id: str, part_ind: int, output_path: Path, overwrite_existing: bool):
        self.processor_id = processor_id
        self.part_ind = part_ind
        self.output_path = output_path
        self.is_overwrite_existing = overwrite_existing
        self.output_path.mkdir(parents=True, exist_ok=True)

    @property
    def name(self):
        return "ResultWriter"

    def process(self, data: Dict[str, Dict[str, Any]], filename: str) -> Dict[str, Any]:
        with open(str((self.output_path / '{filename}-{ind}-{time}.csv'.format(filename=filename,
                                                                               ind=self.part_ind,
                                                                               time=time.time())).absolute()),
                  mode='w') as output:
            output_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for (vid, result) in data.items():
                try:
                    output_writer.writerow([vid] + list(result.items()))
                except Exception:
                    output_writer.writerow([vid, str(result)])

        return {}
