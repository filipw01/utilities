import os
import requests
import boto3
from .email import send_html_email, build_email

client = boto3.client('dynamodb', region_name='eu-central-1')


class VaccineChecker:
    def __init__(self):
        self.vaccineData = None
        self.found = False

    def scrape(self):
        result = client.scan(TableName="vaccineCheck")
        if 'Items' in result:
            credentials = max(result['Items'], key=lambda x: int(x['ttl']['N']))
        else:
            raise ConnectionError(f"Couldn't find credentials in DynamoDB {str(result)}")
        response = requests.get(
            f'https://pacjent.erejestracja.ezdrowie.gov.pl/api/patient/{os.getenv("PATIENT_ID")}',
            headers={
                'x-csrf-token': credentials['csrfToken']['S'],
                'cookie': f'patient_sid={credentials["sessionId"]["S"]}',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'
            }
        ).json()
        if 'patientData' not in response:
            error_message = f"Couldn't connect to the IKP API '{str(response)}'"
            send_html_email(build_email(error_message))
            raise ConnectionError(error_message)
        if len(response.keys()) > 1:
            self.vaccineData = response
            email = build_email(self.prepare_email_content())
            send_html_email(email)
            return f"Found prescription ({str(response)})"
        return f"No prescription ({str(response)})"

    def prepare_email_content(self):
        email = '<h1>Vaccine</h1>'
        email += '<b style="color: red">'
        for (key, value) in self.vaccineData.items():
            email += f'{key} - {str(value)}<br/>'
        email += '</b>'
        return email
