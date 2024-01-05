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

    reverse_geocoding_input = input()

    command_list.append(reverse_geocoding_input)

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
    reverse_attribution = False

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
            weather_obj = generate_json.NWSAPI(f"{lat} {lon}").return_weather_object()
        except TypeError:
            return False  # Exit main() w/o sys.exit(0)

        try:
            WeatherInfo = get_data_from_json.WeatherQuery(weather_obj)
        except (AttributeError, TypeError):
            return False  # Exit main() w/o sys.exit(0)

    for command in command_list[2:-1]:
        weather_query_input_list = command.split(" ")
        try:
            if 'TEMPERATURE AIR' in command:
                results_list.append(
                    WeatherInfo.air_temp(weather_query_input_list[-3], int(weather_query_input_list[-2]),
                                         weather_query_input_list[-1]))

            elif 'TEMPERATURE FEELS' in command:
                results_list.append(
                    WeatherInfo.feels_like(weather_query_input_list[-3], int(weather_query_input_list[-2]),
                                           weather_query_input_list[-1]))

            elif 'HUMIDITY' in command:
                results_list.append(WeatherInfo.humidity_or_precipitation(int(weather_query_input_list[-2]),
                                    weather_query_input_list[-1], 'h'))

            elif 'WIND' in command:
                results_list.append(
                    WeatherInfo.wind_speed(int(weather_query_input_list[-2]), weather_query_input_list[-1]))

            elif 'PRECIPITATION' in command:
                results_list.append(WeatherInfo.humidity_or_precipitation(int(weather_query_input_list[-2]),
                                    weather_query_input_list[-1], 'p'))
            else:
                continue
        except TypeError:
            continue

    reverse_geocoding_input = command_list[-1]
    reverse_geocoding_input_list = reverse_geocoding_input.split(" ")

    if 'FILE' in reverse_geocoding_input:
        reverse_location_obj = (generate_json.File(" ".join(reverse_geocoding_input_list[2:])).
                                return_info_obj())

        try:
            TargetDisplay = get_data_from_json.ReverseGeocoding(reverse_location_obj).return_location()
        except TypeError:
            return False  # Exit main() w/o sys.exit(0)

    else:
        reverse_attribution = True
        lat, lon = WeatherInfo.return_location()

        reverse_location_obj = generate_json.NominatimReverseAPI(f"{lat} {lon}").return_info_obj()

        try:
            TargetDisplay = get_data_from_json.ReverseGeocoding(reverse_location_obj).return_location()
        except TypeError:
            return False  # # Exit main() w/o sys.exit(0)

    results_list.append(TargetDisplay)

    # Output results
    print(results_list[0])  # Latitude and longitude
    print(results_list[-1])  # Display address

    if 'FAILED' in results_list:
        start_fail_index = results_list.index('FAILED')  # When first error message starts

        for i in range(results_list.index('FAILED'), start_fail_index+3):  # Entirety of first error message
            print(results_list[i])
    else:
        for i in results_list[1:-1]:  # Results from queries
            print(i)

    # Output attribution
    if forward_attribution:
        print("**Forward geocoding data from OpenStreetMap")
    if reverse_attribution:
        print("**Reverse geocoding data from OpenStreetMap")
    if weather_attribution:
        print("**Real-time weather data from National Weather Service, United States Department of Commerce")


if __name__ == "__main__":
    main()
