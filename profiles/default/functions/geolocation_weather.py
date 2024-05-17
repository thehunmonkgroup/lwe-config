import requests

from lwe.core.tool import Tool

class GeolocationWeather(Tool):

    def get_weather(self, latitude: int, longitude: int, foo: str = 'bar') -> dict:
        url = f'https://wttr.in/{latitude},{longitude}?format=%C|%t'
        response = requests.get(url)
        return response.text

    def __call__(self, latitude: int, longitude: int) -> dict:
        """
        Get weather for a location based on latitutde and longitude

        :param latitude: The latitude of the location.
        :type latitude: int
        :param longitude: The longitude of the location.
        :type longitude: int
        :return: A dictionary containing the weather data.
        :rtype: dict

        """
        try:
            weather_data = self.get_weather(latitude, longitude)
            condition, temperature = weather_data.split('|')
            output = {
                'weather': {
                    'condition': condition,
                    'temperature': temperature
                },
                'message': f"Retrieved weather for {latitude}, {longitude}",
            }
        except Exception as e:
            output = {
                'error': f"Failed to get weather: {e}",
            }
        return output
