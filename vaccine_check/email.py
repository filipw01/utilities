from datetime import date
import boto3
from botocore.exceptions import ClientError


def send_html_email(html):
    client = boto3.client('ses', region_name='eu-central-1')

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': ["wachowiakf@gmail.com"]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': html
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': f'Vaccine checker - {date.today()}'
                }
            },
            Source='Vaccine checker <wachowiakf@gmail.com>'
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
