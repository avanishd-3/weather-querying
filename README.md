# weather-querying

Installation Instructions
1. git clone https://github.com/avanishd-3/weather-querying
2. pip install -r requirements.txt


Querying Nominatim and Open Meteo for weather information for any location on Earth.

First line of input (choose 1):
1. TARGET NOMINATIM location -> location is any arbitrary, non-empty string describing the target location
2. TARGET FILE path -> path is the path to a file stored locally, containing the result of a previous call to Nominatim

Second line of input (choose 1):
1. WEATHER API -> use the Open Meteo API to obtain hourly weather forecasts.
2. WEATHER FILE path -> path is the path to a file stored locally, containing the result of a previous call to the National Weather Service's API for obtaining an hourly weather forecast
   1. Note this only works for locations inside the U.S.

Other lines -> Specify weather query

1. TEMPERATURE AIR scale length limit -> air temperature
      1. scale: F or C
      2. length: number of hours into the future for which the query is being made
      3. limit: MAX or MIN
2. TEMPERATURE FEELS scale length limit -> "feels like" air temperature
      1. scale: F or C 
      2. length: number of hours into the future for which the query is being made
      3. limit: MAX or MIN
3. HUMIDITY length limit -> relative humidity reported as a percentage
      1. length: number of hours into the future for which the query is being made
      2. limit: MAX or MIN
4. WIND length limit -> wind speed in miles per hour
      1. length: number of hours into the future for which the query is being made
      2. limit: MAX or MIN
5. PRECIPITATION length limit -> hourly chance of precipitation reported as a percentage
      1. length: number of hours into the future for which the query is being made
      2. limit: MAX or MIN
6. NO MORE QUERIES -> stop entering weather queries