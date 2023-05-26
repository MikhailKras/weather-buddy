import pytest

from httpx import AsyncClient


async def test_get_page_weather_search(ac: AsyncClient):
    response = await ac.get("/weather/search")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize(
    "city_input, expected_status, detail, content_type",
    [
        ("Brussels", 200, None, "text/html"),
        ("Invalid_city", 400, "Invalid city!", None)
    ]
)
async def test_find_city_name_matches(
        ac: AsyncClient,
        city_input,
        expected_status,
        detail,
        content_type,
        fill_city_table
):
    response = await ac.get(f"/weather/city_names", params={"city_input": city_input})

    assert response.status_code == expected_status

    if detail:
        assert response.json()["detail"] == detail

    if content_type:
        assert content_type in response.headers["content-type"]


@pytest.mark.parametrize(
    "latitude, longitude, city, expected_status, detail",
    [
        (50.85045, 4.34878, "Brussels", 200, None),
        ("not float", "not float", "search_by_coordinates", 400, "Latitude is not a valid float. Longitude is not a valid float"),
        ("not float", 4.34878, "search_by_coordinates", 400, "Latitude is not a valid float"),
        (50.85045, "not float", "search_by_coordinates", 400, "Longitude is not a valid float"),
        (-100, 200, "search_by_coordinates", 400, "Invalid coordinates!"),
        (0, 0, "search_by_coordinates", 400, "No matching location found."),
        (1, 1, "search_by_coordinates", 400, "No information found for given coordinates"),
    ]
)
async def test_get_city_weather(
        ac: AsyncClient,
        latitude,
        longitude,
        city,
        expected_status,
        detail
):
    response = await ac.get(f"/weather/info", params={"latitude": latitude, "longitude": longitude, "city": city})

    assert response.status_code == expected_status

    if detail:
        assert response.json()["detail"] == detail
