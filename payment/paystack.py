import requests
import json
from requests.exceptions import ReadTimeout, ConnectionError
from django.conf import settings
from utilities.logging_utils import log_error

class Paystack:
    PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co/"
    
    def initialize_payment(self, email, amount):
        path = f'transaction/initialize'
        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SK}",
            'Content-Type': 'application/json',
        }
        url = self.base_url + path
        data = {
            "email": email,
            "amount": int(amount) * 100, # Paystack requirement
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
        except (ReadTimeout, ConnectionError):
            return 500, # this is to simulate error 500
        
        if response.status_code == 200:
            log_error(f'paystack status code {response.status_code} with response -- {response.json()}')
            response_data = response.json()
            return response.status_code, response_data['data']['access_code'], response_data['data']['reference']
        else:
            log_error(f'paystack initiate payment status code {response.status_code} \n with response -- {response.json()}')
            return response.status_code,

    def verify_payment(self, ref, *args, **kwargs):
        path = f'transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)
        response_data = response.json()
        if response.status_code == 200 and response_data['data']['status'] == 'success':            
            return response_data['status'], response_data['data']
        else:
            log_error(f'paystack verify payment status code {response.status_code} \n with response -- {response.json()}')

        response_data = response.json()

        return response_data['status'], response_data['message']