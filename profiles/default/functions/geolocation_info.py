import requests

from lwe.core.function import Function

class GeolocationInfo(Function):

    def get_public_ip(self):
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']

    def get_location_info(self, ip):
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        return response.json()

    def __call__(self, banner: str = "No banner") -> dict:
        """
        Retrieve information for the current location

        :param banner: A banner to display above the content.
        :type banner: str
        :return: A dictionary containing information for the current location.
        :rtype: dict
        """
        try:
            public_ip = self.get_public_ip()
            location_info = self.get_location_info(public_ip)
            output = {
                'message': 'Retrieved information for current location',
                'banner': banner,
                'public_ip': public_ip,
                'location_info': location_info,
            }
        except Exception as e:
            output = {
                'error': f"Failed to retrieve information for current location: {e}",
            }
        return output
