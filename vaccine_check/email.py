from datetime import date
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ses', region_name='eu-central-1')


def build_email(email_content):
    return f'''
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email</title>
            <style>
                body {{
                    background-color: #fff;
                }}
                table {{
                    margin: auto;
                }}
                h1{{
                    font-size: 1.5rem;
                }}
            </style>
        </head>
        <body>
            <table border="0" cellpadding="0" cellspacing="0" width="600">
            <tr>
                <td align="center" valign="top">
                    {email_content}
                </td>
            </tr>
        </body>
        </html>
        '''


def send_html_email(html):
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
