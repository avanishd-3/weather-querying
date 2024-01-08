import statistics

import pandas as pd

import temperature_formulas
import time_conversion


class ForwardGeocoding:
    def __init__(self, geo_obj: dict):
        self.geo_obj = geo_obj

    def return_location(self) -> str:
        """ Return location in latitude longitude format"""

        latitude_float = float(self.geo_obj[0]['lat'])  # B/c Nominatim returns output as a giant array
        latitude = f'{latitude_float}/N' if latitude_float > 0 else f'{-latitude_float}/S'

        longitude_float = float(self.geo_obj[0]['lon'])  # B/c Nominatim returns output as a giant array
        longitude = f'{longitude_float}/E' if longitude_float > 0 else f'{-longitude_float}/W'

        return f'{latitude} {longitude}'



class OpenMeteoQuery:

    def __init__(self, weather_obj: pd.DataFrame):
        self.weather_obj = weather_obj

    def return_info(self, *scale: str, length: int, limit: str, query_type: str):

        match query_type:
            case 'air temp':
                index_str = 'temperature_2m'
            case 'feels like temp':
                index_str = 'apparent_temperature'
            case 'wind speed':
                index_str = 'wind_speed_10m'
            case 'humidity':
                index_str = 'relative_humidity_2m'
            case 'precipitation':
                index_str = 'precipitation_probability'
            case _:
                index_str = 'temperature_2m'

        range_limit = length if length < len(self.weather_obj.index) else len(self.weather_obj.index)

        new_hourly_dataframe = self.weather_obj.head(range_limit)

        match limit:
            case 'MAX':
                idx = new_hourly_dataframe.idxmax()[index_str]
                row = new_hourly_dataframe.iloc[idx]

            case 'MIN':
                idx = new_hourly_dataframe.idxmin()[index_str]
                row = new_hourly_dataframe.iloc[idx]

            case _:
                row = new_hourly_dataframe.iloc[0]

        match query_type:
            case 'humidity' | 'precipitation':
                return f"{row['date']} {row[index_str]:.4f}%"
            case _:
                if scale == 'F' or scale == 'I':
                    return f"{row['date']} {temperature_formulas.convert_to_us(row[index_str], query_type):.4f}"
                else:
                    return f"{row['date']} {row[index_str]:.4f}"


class WeatherQuery:

    def __init__(self, weather_obj: dict):
        self.weather_obj = weather_obj

    def return_location(self) -> (float, float):
        """ Return latitude and longitude of NWS weather station"""
        coordinates = self.weather_obj["geometry"]["coordinates"][0]

        unique_coordinates = list(set(list(map(tuple, coordinates))))  # List of unique tuples

        lon_list = [unique_coordinates[i][0] for i in range(0, len(unique_coordinates))]
        lat_list = [unique_coordinates[i][1] for i in range(0, len(unique_coordinates))]

        lon = statistics.fmean(lon_list)
        lat = statistics.fmean(lat_list)

        return lat, lon

    def temp_or_wind(self, scale: str, length: int, limit: str, a_or_f_or_w: str) -> str:
        """ Return max/min feels like temperature, air temperature, or wind speed over given period of time"""

        range_limit = length if length < len(self.weather_obj) else len(self.weather_obj)

        temp_list = [float(self.weather_obj["properties"]["periods"][i]['temperature'])
                     for i in range(0, range_limit)]
        
        hours_list = [self.weather_obj["properties"]["periods"][i]['startTime'] for i in range(0, range_limit)]

        wind_list = [self.weather_obj["properties"]["periods"][i]['windSpeed'] for i in range(0, range_limit)]
        wind_list = [float(i.split(" ")[0]) for i in wind_list]  # Chop off mph from wind speed

        if a_or_f_or_w == 'f':
            humidity_list = [float(self.weather_obj["properties"]["periods"][i]['relativeHumidity']['value'])
                             for i in range(0, range_limit)]
            info_temp_list = [temperature_formulas.calc_feels_like_temp(temp_list[i], humidity_list[i],
                              wind_list[i]) for i in range(0, len(temp_list))]
        else:
            info_temp_list = temp_list

        if scale == 'C':
            info_temp_list = [temperature_formulas.convert_to(i, 'C') for i in info_temp_list]

        if a_or_f_or_w == 'w':
            weather_dict = dict(zip(wind_list, hours_list))
        else:
            weather_dict = dict(zip(info_temp_list, hours_list))

        match limit:
            case 'MAX':
                max_val = max(info_temp_list)
                nws_time = "".join(weather_dict[max_val].split(":")[0])
                iso_time = time_conversion.nws_to_iso_time(nws_time)
                return f'{iso_time} {max_val:.4f}'  # Only 4 decimal places

            case 'MIN':
                min_val = min(info_temp_list)
                nws_time = "".join(weather_dict[min_val].split(":")[0])
                iso_time = time_conversion.nws_to_iso_time(nws_time)
                return f'{iso_time} {min_val:.4f}'  # Only 4 decimal places

    def humidity_or_precipitation(self, length: int, limit: str, h_or_p: str) -> str:
        """ Return humidity or precipitation(%) over given period of time"""
        h_or_p = 'relativeHumidity' if h_or_p == 'h' else 'probabilityOfPrecipitation'

        range_limit = length if length < len(self.weather_obj) else len(self.weather_obj)

        info_list = [float(self.weather_obj["properties"]["periods"][i][h_or_p]['value'])
                     for i in range(0, range_limit)]
        hours_list = [self.weather_obj["properties"]["periods"][i]['startTime'] for i in range(0, range_limit)]

        weather_dict = dict(zip(info_list, hours_list))

        match limit:
            case 'MAX':
                max_val = max(info_list)
                nws_time = "".join(weather_dict[max_val].split(":")[0])
                iso_time = time_conversion.nws_to_iso_time(nws_time)
                return f'{iso_time} {max_val:.4f}%'  # Only 4 decimal places and a percentage

            case 'MIN':
                min_val = min(info_list)
                nws_time = "".join(weather_dict[min_val].split(":")[0])
                iso_time = time_conversion.nws_to_iso_time(nws_time)
                return f'{iso_time} {min_val:.4f}%'  # Only 4 decimal places and a percentage


class ReverseGeocoding:
    def __init__(self, geo_obj: dict):
        self.geo_obj = geo_obj

    def return_location(self) -> str:
        """ Return address location"""

        return self.geo_obj['display_name']
