import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("city_id", range(2000, 10000))
async def test_get_city_weather(
        ac: AsyncClient,
        city_id,
        fill_city_table_with_real_data
):
    response = await ac.get(f"/weather/info?city_id={city_id}")
    assert response.status_code == 200
