from typing import Callable
from urllib import request


class JobsPage:
    def __init__(
            self,
            url: str,
            jobs_parser: Callable) -> None:
        self.url = url
        self.page_text = None
        self._jobs_parser = jobs_parser


    def load(self):
        resp = request.get(url=self.url)
        assert resp.status_code == 200
        self.page_text = resp.text
