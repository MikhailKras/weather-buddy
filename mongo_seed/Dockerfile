FROM mongo:6.0.6

WORKDIR /data

COPY . .

ARG MONGO_INITDB_ROOT_USERNAME
ARG MONGO_INITDB_ROOT_PASSWORD

ENV MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}
ENV MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}

CMD mongoimport --host mongodb --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db weather_buddy --collection new_clothing_data --type json --file weather_buddy.new_clothing_data.json --jsonArray && \
    mongoimport --host mongodb --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db weather_buddy --collection weatherapi_codes --type json --file weather_buddy.weatherapi_codes.json --jsonArray
