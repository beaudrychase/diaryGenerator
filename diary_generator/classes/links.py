from abc import ABC, abstractmethod

import fitz


class Links(ABC):

    @abstractmethod
    def render(self, page: fitz.Page, page_number: int):
        pass
