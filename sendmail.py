import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "joy.choco.banana@gmail.com"  # Enter your address
receiver_email = "rohogoho@gmail.com"  # Enter receiver address
password = "sweatyellow"
message = """\
Subject: Test3

Good morning, Danang
This message is sent from Python."""


context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    try:
        server.login(sender_email, password)
    except smtplib.SMTPAuthenticationError as e:
        if e.smtp_code == 535:
            err = """
            Possible Authentication Error:
            - Username and Password are not match
            - Your 2-Step Verification is enabled
            - Your Less-Secure-Authentication is disabled (if gmail, you can visit this https://www.google.com/settings/security/lesssecureapps)
            """
            raise BaseException(err)
    except Exception as e:
        raise e
    server.sendmail(sender_email, receiver_email, message)