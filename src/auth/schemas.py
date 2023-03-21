from pydantic import BaseModel, validator
import geonamescache


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    city: str

    @validator('city')
    def city_must_be_valid(cls, city_input):
        gc = geonamescache.GeonamesCache()
        city_info = gc.get_cities_by_name(city_input.title())
        if not city_info:
            raise ValueError('Invalid city')
        return city_input
