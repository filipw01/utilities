from datetime import date
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ses', region_name='eu-central-1')


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


def build_html_email(elements):
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
                a {{
                    display: block;
                    margin: 2rem 0;
                    font-family: system-ui;
                    text-decoration: none;
                    color: black;
                }}
                img{{
                    display: block;
                    width: 100%;
                }}
                h1{{
                    font-size: 1.5rem;
                }}
                h1, p{{
                    display: block;
                    margin: 1rem 0;
                }}
            </style>
        </head>
        <body>
            <table border="0" cellpadding="0" cellspacing="0" width="600">
            <tr>
                <td align="center" valign="top">
                    {''.join(elements)}
                </td>
            </tr>
        </body>
        </html>
        '''
