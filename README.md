# Weather-Querying
Querying Nominatim and National Weather Service for weather information for any location in the U.S.

The first thing the program does is read several lines of input that describe the job you want it to do. 

First line of input:
   a. TARGET NOMINATIM location -> location is any arbitrary, non-empty string describing the target location
   b. TARGET FILE path -> path is the path to a file stored locally, containing the result of a previous call to Nominatim

Second line of input:
   a. WEATHER NWS -> use the National Weather Service API to obtain hourly weather forecasts.
   b. WEATHER FILE path -> path is the path to a file stored locally, containing the result of a previous call to the National Weather Service's API for obtaining an hourly weather forecast

Other lines -> Soecify weather query

   a. TEMPERATURE AIR scale length limit -> air temperature
      scale: F or C
      length: number of hours into the future for which the query is being made
      limit: MAX or MIN
    b. TEMPERATURE FEELS scale length limit -> "feels like" air temperature
       scale: F or C
       length: number of hours into the future for which the query is being made
       limit: MAX or MIN
    c. HUMIDITY length limit -> relative humidity reported as a percentage
       length: number of hours into the future for which the query is being made
       limit: MAX or MIN
    d. WIND length limit -> wind speed in miles per hour
       length: number of hours into the future for which the query is being made
       limit: MAX or MIN
    e. PRECIPITATION length limit -> hourly chance of precipitation reported as a percentage
       length: number of hours into the future for which the query is being made
       limit: MAX or MIN

Continue reading weather queries until input line is NO MORE QUERIES

Final line of input:
     a. REVERSE NOMINATIM -> use Nominatim API to do reverse geocoding (determine a description of where the nearest weather station is located based on latitude and longitude)
     b. REVERSE FILE path -> use a file stored locally containing the results of previous calls to Nominatim's reverse geocoding API instead
