#!/bin/bash

pytest tests -v -s -W ignore::DeprecationWarning -k "not database_city_weather_info"
