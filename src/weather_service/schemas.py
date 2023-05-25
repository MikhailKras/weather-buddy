from typing import List

from pydantic import BaseModel


class CityInDB(BaseModel):
    id: int
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    population: int
    timezone: str
    alternatenames: List[str]
