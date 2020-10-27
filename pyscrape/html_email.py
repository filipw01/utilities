import os
from smtplib import SMTP
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_html_email(html):
    server = SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(os.getenv("EMAIL_USERNAME"), os.getenv("EMAIL_PASSWORD"))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Bankier - {date.today()}"
    msg.attach(MIMEText(html, "html"))

    server.sendmail("news@bankier.pl", "wachowiakf@gmail.com", msg.as_string())
    server.quit()


def build_html_email(articles):
    body = ""
    for link, img_src, title, lead in articles:
        body += f"""
                <a href="{link}">
                    <img src="{img_src}"/>
                    <h1>{title}</h1>
                    <p>{lead}</p>
                </a>
                """

    return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email</title>
            <style>
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
                    {body}
                </td>
            </tr>
        </body>
        </html>
        """
