from dataclasses import dataclass


@dataclass
class JobInfo:
    title: str = None
    location: str = None
    url: str = None
    description: str = None
