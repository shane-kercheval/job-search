from dataclasses import dataclass
import pandas as pd


@dataclass
class JobInfo:
    company: str = None
    title: str = None
    location: str = None
    url: str = None
    description: str = None


def to_dataframe(jobs: list[JobInfo]) -> pd.DataFrame:
    return pd.DataFrame(dict(
        company=[j.company for j in jobs],
        title=[j.title for j in jobs],
        location=[j.location for j in jobs],
        url=[j.url for j in jobs],
        description=[j.description for j in jobs],
    ))


def from_dataframe(df: pd.DataFrame) -> list[JobInfo]:
    def to_info(row):
        return JobInfo(
            company=row.company,
            title=row.title,
            location=row.location,
            url=row.url,
            description=row.description,
        )
    x = df.apply(lambda x: to_info(x), axis=1)
    return x.tolist()
