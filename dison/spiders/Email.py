import smtplib
from email.mime.text import MIMEText as text
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

class Email:
  user = None

  def __init__(self, user):
    self.user = user

  def run(self):
    self.sendmail()

  def sendmail(self):
    from_address= self.user['email']

    smtp_server = 'smtp.gmail.com'
    smtp_port= 587
    smtp_user= self.user['email']
    smtp_password= self.user['password']

    msg = MIMEMultipart()
    msg.attach(MIMEText('New book data', "plain"))
    msg['Subject'] = "New books"
    msg['From'] = self.user['email']
    msg['To'] = 'isebarn182@gmail.com'

    filename = "data.csv"

    with open(filename, "rb") as attachment:
      # Add file as application/octet-stream
      # Email client can usually download this automatically as attachment
      part = MIMEBase("application", "octet-stream")
      part.set_payload(attachment.read())

    encoders.encode_base64(part)
    msg.attach(part)
    text = msg.as_string()

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )


    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(self.user['email'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
  email = Email({'email': 'isebarn.data@gmail.com', 'password': 'tommy182'})
  email.run()


# https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp
