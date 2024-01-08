import generate_json
import get_data_from_json


def _get_commands() -> list:
    """ Return list containing all commands user inputs"""
    command_list = []

    target_input = input()
    command_list.append(target_input)

    weather_input = input()

    command_list.append(weather_input)

    while True:
        weather_query_input = input()

        if weather_query_input == 'NO MORE QUERIES':
            break
        else:
            command_list.append(weather_query_input)

    return command_list


def main() -> None | bool:
    """ Take input and print output for searches
        Return False and print error output if API query or file reading is unsuccessful or
        returns invalid format"""

    # Get all input from user
    command_list = _get_commands()

    # Default is not printing attribution
    forward_attribution = False
    weather_attribution = False

    target_input = command_list[0]
    target_input_list = target_input.split(" ")

    results_list = []  # To store output to print

    if 'FILE' in target_input_list:
        location_obj = generate_json.File(" ".join(target_input_list[2:])).return_info_obj()
        try:
            FileForwardGeoCoding = get_data_from_json.ForwardGeocoding(location_obj).return_location()
        except TypeError:
            return False  # Exit main() w/o sys.exit(0)
    else:
        forward_attribution = True

        loc = ("+".join(target_input_list[2:])).replace(',', '')  # Make location web searchable
        location_obj = generate_json.NominatimForwardAPI(loc).return_info_obj()

        try:
            FileForwardGeoCoding = get_data_from_json.ForwardGeocoding(location_obj).return_location()
        except (TypeError, IndexError):
            return False  # Exit main() w/o sys.exit(0)

    results_list.append(f'TARGET {FileForwardGeoCoding}')

    weather_input = command_list[1]
    weather_input_list = weather_input.split(" ")

    if 'FILE' in weather_input_list:
        weather_obj = generate_json.File(" ".join(weather_input_list[2:])).return_info_obj()
        try:
            WeatherInfo = get_data_from_json.WeatherQuery(weather_obj)
        except TypeError:
            return False  # Exit main() w/o sys.exit(0)
    else:
        weather_attribution = True

        lat_and_lon_info = FileForwardGeoCoding.split(" ")
        lat = float(lat_and_lon_info[0][:-2])

        if lat_and_lon_info[0][-1] == 'S':
            lat = -lat

        lon = float(lat_and_lon_info[1][:-2])
        if lat_and_lon_info[1][-1] == 'W':
            lon = -lon

        try:
            weather_obj = generate_json.OpenMeteoAPI(f"{lat} {lon}").return_weather_object()
        except TypeError:
            return False  # Exit main() w/o sys.exit(0)

        try:
            WeatherInfo = get_data_from_json.OpenMeteoQuery(weather_obj)
        except (AttributeError, TypeError):
            return False  # Exit main() w/o sys.exit(0)

    for command in command_list[2:]:
        weather_query_input_list = command.split(" ")
        try:
            if 'TEMPERATURE AIR' in command:
                results_list.append(WeatherInfo.return_info(weather_query_input_list[-3],
                                                            length=int(weather_query_input_list[-2]),
                                                            limit=weather_query_input_list[-1],
                                                            query_type='air temp'))

            elif 'TEMPERATURE FEELS' in command:
                results_list.append(WeatherInfo.return_info(weather_query_input_list[-3],
                                                            length=int(weather_query_input_list[-2]),
                                                            limit=weather_query_input_list[-1],
                                                            query_type='feels like temp'))

            elif 'HUMIDITY' in command:
                results_list.append(WeatherInfo.return_info(length=int(weather_query_input_list[-2]),
                                                            limit=weather_query_input_list[-1],
                                                            query_type='humidity'))

            elif 'WIND' in command:
                results_list.append(WeatherInfo.return_info('F',
                                    length=int(weather_query_input_list[-2]),
                                    limit=weather_query_input_list[-1], query_type='wind speed'))

            elif 'PRECIPITATION' in command:
                results_list.append(WeatherInfo.return_info(length=int(weather_query_input_list[-2]),
                                                            limit=weather_query_input_list[-1],
                                                            query_type='precipitation'))
            else:
                continue
        except TypeError:
            continue

    # Output results

    print(results_list[0])  # Latitude and longitude

    if 'FAILED' in results_list:
        start_fail_index = results_list.index('FAILED')  # When first error message starts

        for i in range(results_list.index('FAILED'), start_fail_index+3):  # Entirety of first error message
            print(results_list[i])
    else:
        for i in results_list[1:]:  # Results from queries
            print(i)

    # Output attribution
    if forward_attribution:
        print("**Forward geocoding data from OpenStreetMap")
    if weather_attribution:
        print("**Weather data from https://open-meteo.com/")


if __name__ == "__main__":
    main()
