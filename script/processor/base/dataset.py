# from typing import
from processor.base.extractor import Extractor
from processor.base.downloader import Downloader
from processor.base.transformer import Transformer
from processor.base.writer import Writer


class Dataset:

    def __init__(self):
        self.__downloaders = []
        self.__transformers = []
        self.__writers = []
        self.__extractors = []
        self.__memory_results = {}

    def append_extractor(self, extractor: Extractor) -> None:
        self.__extractors.append(extractor)

    def append_downloader(self, downloader: Downloader) -> None:
        self.__downloaders.append(downloader)

    def append_transformer(self, transformer: Transformer) -> None:
        self.__transformers.append(transformer)

    def append_writers(self, writer: Writer) -> None:
        self.__writers.append(writer)

    def process(self) -> None:
        for extractor in self.__extractors:
            self.__memory_results[extractor.name] = extractor.process(self.__memory_results)

            for writer in self.__writers:
                writer.process(self.__memory_results[extractor.name], extractor.name)

        for downloader in self.__downloaders:
            self.__memory_results[downloader.name] = downloader.process(self.__memory_results)

            for writer in self.__writers:
                writer.process(self.__memory_results[downloader.name], downloader.name)

        for transformer in self.__transformers:
            self.__memory_results[transformer.name] = transformer.process(self.__memory_results)

            for writer in self.__writers:
                writer.process(self.__memory_results[transformer.name], transformer.name)

