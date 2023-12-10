def calc_feels_like_temp(temp: float, humidity: float, wind: float) -> float:
    """ Given temperature in Fahrenheit, humidity in percentage, wind speed in miles per hour
        Return feels like temperature in Fahrenheit"""
    if temp >= 68:
        heat_index_first_part = -42.379 + 2.04901523*temp + 10.14333127*humidity - 0.22475541*temp*humidity
        heat_index_second_part = -0.00683783*(temp**2)-0.05481717*(humidity**2) + 0.00122874*(temp**2)*humidity
        heat_index_third_part = 0.00085282*temp*(humidity**2)-0.00000199*(temp**2)*(humidity**2)

        heat_index = heat_index_first_part + heat_index_second_part + heat_index_third_part

        return heat_index

    elif temp < 50 and wind > 3:
        return 35.74 + 0.6215*temp - 35.75*(wind**0.16)+0.4275*temp*(wind**0.16)
    else:
        return temp


def convert_to(temp: float, unit: str) -> float:
    """ Covert temperature scale to unit given """
    if unit == 'C':
        return (temp-32)*5/9  # Temperature in Celsius
    else:
        return (temp*9/5) + 32  # Temperature in Fahrenheit
