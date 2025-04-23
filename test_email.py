from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "ankitnayak7895@gmail.com"
app.config["MAIL_PASSWORD"] = "veyq pvza ntcm eqse"
app.config["MAIL_DEFAULT_SENDER"] = "ankitnayak7895@gmail.com"

mail = Mail(app)

with app.app_context():
    msg = Message("Test Email", recipients=["ankitnayak7895@gmail.com"])
    msg.body = "This is a test email from Flask."
    try:
        mail.send(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Test email failed: {e}")

