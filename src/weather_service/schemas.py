import datetime
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator


class CityInDB(BaseModel):
    id: int
    name: str
    region: Optional[str]
    country: str
    latitude: float
    longitude: float
    population: int
    timezone: str
    alternatenames: List[str]


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ClothingItem(BaseModel):
    clothingItems: List[str]


class ClothingLayers(BaseModel):
    BaseLayer: ClothingItem
    MidLayer: ClothingItem
    OuterLayerShell: ClothingItem
    Accessories: ClothingItem


class PrecipitationClothing(BaseModel):
    UpperBody: ClothingLayers
    LowerBody: ClothingLayers
    Footwear: ClothingItem


class Precipitation(BaseModel):
    none: PrecipitationClothing = Field(..., alias='None')
    Rain: Optional[PrecipitationClothing]
    Snow: Optional[PrecipitationClothing]


class TemperatureRange(BaseModel):
    min: int
    max: int


class ClothesDataDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    temperatureRange: TemperatureRange
    precipitation: Precipitation

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    schema_extra = {
        "example": {
            "_id": "64834ea1fda0d16eceebf0ca",
            "temperatureRange": {"min": 10, "max": 15},
            "precipitation": {
                "None": {
                    "UpperBody": {
                        "BaseLayer": {"clothingItems": ["Light long-sleeve shirt"]},
                        "MidLayer": {"clothingItems": ["Light sweater"]},
                        "OuterLayerShell": {"clothingItems": []},
                        "Accessories": {"clothingItems": ["Scarf"]},
                    },
                    "LowerBody": {
                        "BaseLayer": {"clothingItems": ["Light pants"]},
                        "MidLayer": {"clothingItems": []},
                        "OuterLayerShell": {"clothingItems": []},
                        "Accessories": {"clothingItems": []},
                    },
                    "Footwear": {"clothingItems": ["Sneakers"]},
                },
                "Rain": {
                    "UpperBody": {
                        "BaseLayer": {"clothingItems": ["Light long-sleeve shirt"]},
                        "MidLayer": {"clothingItems": ["Light sweater", "Raincoat"]},
                        "OuterLayerShell": {"clothingItems": []},
                        "Accessories": {"clothingItems": ["Scarf"]},
                    },
                    "LowerBody": {
                        "BaseLayer": {"clothingItems": ["Light pants"]},
                        "MidLayer": {"clothingItems": []},
                        "OuterLayerShell": {"clothingItems": []},
                        "Accessories": {"clothingItems": []},
                    },
                    "Footwear": {"clothingItems": ["Sneakers", "Rain boots"]},
                },
            },
        }
    }


class PrecipitationType(Enum):
    none = "None"
    rain = "Rain"
    snow = "Snow"


class CitySearchHistory(BaseModel):
    id: Optional[int]
    user_id: int
    city_id: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    request_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        validate_assignment = True
        extra = 'forbid'

        @validator('id', 'request_at', pre=True)
        def prevent_assignment(cls, v):
            if v is not None:
                raise ValueError('Assignment not allowed for id and request_at fields')
            return v
