#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class Create:
    def __init__(self):
        
        self.rate_limit_remaining = 0 # Number of requests remaining
        self.rate_limit_reset = None # Datetime when new requests will be available

    def request(self, url, parameters={}, headers={}, file_type='json'):
        """Executes a request to GitHub API.

        Args:
            url: String representing the GitHub API url to be requested.
            parameters: Dictionary of GET parameters to be used in the request.
            headers: Dictionary representing an HTTP header to be used in the request.
            file_type: String representing the type of data to be returned after
                the request. The available types are 'json' and 'text'.
        Returns:
            By default, it returns a JSON dictionary. If file_type='text' is 
            specified, then it returns a string.
        Note:
            To increase the number of possible requests to the GitHub API,
            we add access tokens to the header of our request using 
            environment variables.

            Create your own access tokens following the tutorial below:
            https://developer.github.com/v3/auth/
            And use the environment variables GITHUB_USER and GITHUB_TOKEN
            to store them in your operating system.
        """
        
        try:
            session = requests.Session()
            # session.auth = (os.getenv('GITHUB_USER'), os.getenv('GITHUB_TOKEN'))
            retries = Retry(total = 10)
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(url, params=parameters, headers=headers)
            
            if response.status_code != 200:
                raise Exception("Problem in connection with GitHub API (Status: " + str(response.status_code) + ").")

            self.verify_rate_limit(response.headers)

            if file_type == 'json':
                return response.json()
            if file_type == 'text':   
                return response.text

        except Exception as exception:
            raise(exception)

    def verify_rate_limit(self, header):
        """Guarantees that there is a limit of requests remaining to the GitHub API.

        The number of requests to the GitHub API is limited by GitHub, even with
        authentication. This method verifies the number of requests remaining and
        holds the process for thirty seconds until it receives the permission
        to execute new requests.

        Args:
            header: Dictionary representing the header of the last request made
                in the GitHub API.
        """

        if 'X-RateLimit-Remaining' in header and 'X-RateLimit-Reset' in header:
            self.rate_limit_remaining = int(header.get('X-RateLimit-Remaining'))
            self.rate_limit_reset = int(header.get('X-RateLimit-Reset'))

            datetime_format = '%Y-%m-%d %H:%M:%S'
            reset_time = datetime.fromtimestamp(self.rate_limit_reset).strftime(datetime_format)
            current_time = datetime.now().strftime(datetime_format)
            minutes_remaining = int((datetime.fromtimestamp(self.rate_limit_reset) - datetime.now()).total_seconds() / 60)

            if self.rate_limit_remaining <= 1:
                if reset_time >= current_time:
                    raise ConnectionError("Sorry, our request limit for GitHub API is over. Wait " + str(minutes_remaining) +  " minutes and try again.")
