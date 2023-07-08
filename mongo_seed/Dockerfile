FROM mongo:6.0.6

WORKDIR /data

COPY . .

CMD mongoimport --host mongodb --db weather_buddy --collection new_clothing_data --type json --file weather_buddy.new_clothing_data.json --jsonArray && \
    mongoimport --host mongodb --db weather_buddy --collection weatherapi_codes --type json --file weather_buddy.weatherapi_codes.json --jsonArray
