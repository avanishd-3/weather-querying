import urllib.request
import urllib.error
import json
import time


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
        info = open(loc, 'r')
        info_obj = json.load(info)
        info.close()
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


def _query_apis(url: str, api_type: str) -> dict | bool:
    """ Return dictionary representation of API Query if successful
        If unsuccessful, return False to exit main program"""

    response = None

    try:
        if api_type == 'n':
            hdr = {'Referer': 'adavulur'}  # Nominatim Header
        else:
            hdr = {'User-Agent': 'adavulur@uci.edu', 'Accept': 'application/geo+json'}  # NWS Header

        request = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(request)  # Open URL and read response
        return json.load(response)
    except urllib.error.HTTPError as e:
        print("FAILED")
        print(f'{e.code} {url}')
        print("NOT 200")
        return False  # Exit main program w/o sys.exit(0)
    except urllib.error.URLError:
        print("FAILED")
        print(url)
        print("NETWORK")
        return False  # Exit main program w/o sys.exit(0)
    except json.decoder.JSONDecodeError:
        print("FAILED")
        print(f'200 {url}')
        print("FORMAT")
        return False  # Exit main program w/o sys.exit(0)
    finally:
        if response is not None:
            response.close()
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


class NWSAPI:
    def __init__(self, loc: str):
        self._loc = loc

    def return_weather_object(self) -> dict | bool:
        """ Return dictionary representation of JSON response from NWS API if successful
            If unsuccessful, return False to exit main program"""
        loc_list = self._loc.split(" ")
        lat = loc_list[0]
        lon = loc_list[-1]

        query_loc_url = f'https://api.weather.gov/points/{lat},{lon}'
        loc_info = _query_apis(query_loc_url, 'w')  # Get location info for NWS grid

        grid_id = loc_info['properties']['gridId']
        grid_x = loc_info['properties']['gridX']
        grid_y = loc_info['properties']['gridY']

        final_query_url = f'https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly/?units=us'

        return _query_apis(final_query_url, 'w')
