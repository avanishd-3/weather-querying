import json
import time
import requests

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

""""
Interface

Parameter: loc
           1. File -> Path of nominatim forward data json on local drive 
           2. Geographic location w/ spaces and commas replaced by + to make web searchable
           3. Geographic location represented by longitude and latitude

Method: return_info_obj
        Return dictionary representation of JSON response from file or API
"""


def _return_dict_from_json_file(loc: str) -> dict | bool:
    """ Return dictionary representation of json file if successful
        If unsuccessful, return False to exit main program"""

    try:
        with open(loc, "r") as info:
            info_obj = json.load(info)
    except FileNotFoundError:
        print("FAILED")
        print(loc)
        print("MISSING")
        return False  # Exit main program w/o sys.exit(0)
    except json.decoder.JSONDecodeError:
        print("FAILED")
        print(loc)
        print("FORMAT")
        return False  # Exit main program w/o sys.exit(0)
    else:
        return info_obj


def _query_apis(url: str, api_type: str, *params: dict) -> dict | list | bool:
    """ Return dictionary representation of API Query if successful
        If unsuccessful, return False to exit main program"""

    try:
        if api_type == 'n':
            headers = {'Referer': 'adavulur'}  # Nominatim Header

            request = requests.get(url, headers=headers)
            request.raise_for_status()  # Check for status error

            return request.json()

    except requests.exceptions.HTTPError:
        print("FAILED")
        print(f'{request.status_code} {url}')
        print("NOT 200")
        return False  # Exit main program w/o sys.exit(0)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("FAILED")
        print(url)
        print("NETWORK")
        return False  # Exit main program w/o sys.exit(0)
    except requests.exceptions.JSONDecodeError:
        print("FAILED")
        print(f'200 {url}')
        print("FORMAT")
        return False  # Exit main program w/o sys.exit(0)
    finally:
        if api_type == 'n':
            time.sleep(1)  # Pause for 1 second b/c of Nominatim API rate limit


class File:
    def __init__(self, loc: str):
        self._loc = loc

    def return_info_obj(self) -> dict | bool:
        """ Return dictionary representation of json file for forward geocoding if successful
                If unsuccessful, return False to exit main program"""
        return _return_dict_from_json_file(self._loc)


class NominatimForwardAPI:

    def __init__(self, loc: str):
        self._loc = loc

    def return_info_obj(self) -> dict | bool:
        """ Return dictionary representation of JSON response from Nominatim API for forward geocoding
                   if successful
            If unsuccessful, return False to exit main program"""
        url = f'https://nominatim.openstreetmap.org/search?q={self._loc}&format=json'

        return _query_apis(url, 'n')  # API type is Nominatim


class NominatimReverseAPI:
    def __init__(self, loc: str):
        self._loc = loc

    def return_info_obj(self) -> dict | bool:
        """ Return dictionary representation of JSON response from Nominatim API for reverse geocoding
                   if successful
            If unsuccessful, return False to exit main program"""
        loc_list = self._loc.split(" ")
        lat = loc_list[0]
        lon = loc_list[-1]

        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'

        return _query_apis(url, 'n')  # API type is Nominatim


class OpenMeteoAPI:
    def __init__(self, loc: str):
        self._loc = loc

    def return_weather_object(self) -> pd.DataFrame | bool:
        """ Return dictionary representation of JSON response from NWS API if successful
            If unsuccessful, return False to exit main program"""
        loc_list = self._loc.split(" ")
        lat = loc_list[0]
        lon = loc_list[-1]

        # Set up the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                       "precipitation_probability", "wind_speed_10m"],
            "timezone": "auto",
            "forecast_days": 16
        }

        responses = openmeteo.weather_api(url, params=params)

        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ), "temperature_2m": hourly_temperature_2m, "relative_humidity_2m": hourly_relative_humidity_2m,
            "apparent_temperature": hourly_apparent_temperature,
            "precipitation_probability": hourly_precipitation_probability,
            "wind_speed_10m": hourly_wind_speed_10m}

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        return hourly_dataframe
