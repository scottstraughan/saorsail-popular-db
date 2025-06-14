import json

import requests


class Service:
    def get_repo_info(
        self,
        service_name: str,
        url: str,
        api_key: str = None
    ) -> {}:
        headers = {
            'accept': 'application/json'
        }

        if api_key:
            headers['authorization'] = f'Bearer {api_key}'

        response = requests.get(url, headers=headers)

        if response.status_code in [429, 403]:
            raise RateLimited(f'You have been rated limited by {service_name}.')

        if response.status_code != 200:
            raise SkippableError(f'Unable to fetch repo info from {service_name} ({response.content}).')

        return json.loads(response.content)


class RateLimited(ValueError):
    """
    An error when the service has rate limited the user
    """
    pass


class SkippableError(ValueError):
    """
    An error that we can skip over
    """
    pass
