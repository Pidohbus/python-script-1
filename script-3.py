#!/usr/bin/env python3
"""
Send Vishwakarma Puja greeting emails to multiple Gmail recipients.

SETUP (Gmail requires an App Password, not your normal password):
    1. Turn on 2-Step Verification on the sender Gmail account.
    2. Generate a 16-character App Password:
       https://myaccount.google.com/apppasswords
    3. Install Pillow (used to generate the inline animated GIF):
       pip install pillow
    4. Fill in the CONFIG section below.
    5. Run: python send_vishwakarma_puja_email.py

NOTE ON THE ANIMATION: the script builds a small animated GIF (a spinning
gear) at runtime and embeds it inline in the HTML body. It will animate in
Gmail, Apple Mail, Yahoo, and most mobile clients. Outlook desktop (the
Word-rendering-engine versions) shows only the first frame — that's an
Outlook limitation, not a bug in this script.
"""

import io
import math
import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from PIL import Image, ImageDraw

# ----------------------- CONFIG (edit these) -----------------------
SENDER_EMAIL    = "subhodipnokia@gmail.com"
SENDER_PASSWORD = "mxwr aima tlci guca"   # Gmail App Password, NOT your login password
SENDER_NAME     = "Subhodip"
SENDER_TITLE    = "DevOps Engineer"

RECIPIENTS = [
    
    "riddhimoy.das.97@gmail.com"
]

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
# ---------------------------------------------------------------------

TODAY = date.today().strftime("%d %B %Y")
SUBJECT = "🙏 Happy Vishwakarma Puja!"
GEAR_CID = "gear_animation"  # Content-ID used to reference the inline GIF


def _gear_frame(angle: float, size: int = 120,
                 color=(211, 84, 0), bg=(255, 255, 255)) -> Image.Image:
    """Draw one frame of a spinning gear at the given rotation angle."""
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    outer_r, inner_r, teeth = size * 0.40, size * 0.28, 10
    points = []
    for i in range(teeth * 2):
        a = angle + i * (360 / (teeth * 2))
        r = outer_r if i % 2 == 0 else inner_r
        rad = math.radians(a)
        points.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    draw.polygon(points, fill=color)
    hub_r = size * 0.13
    draw.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r], fill=bg)
    return img


def build_gear_gif(frames: int = 24, size: int = 120) -> bytes:
    """Render a looping spinning-gear animation and return it as GIF bytes."""
    images = [_gear_frame(angle=(360 / frames) * i, size=size) for i in range(frames)]
    buf = io.BytesIO()
    images[0].save(
        buf, format="GIF", save_all=True, append_images=images[1:],
        duration=70, loop=0, disposal=2,
    )
    return buf.getvalue()

PLAIN_BODY = f"""Dear Friend,

Wishing you a very Happy Vishwakarma Puja!

Today, {TODAY}, we celebrate Lord Vishwakarma, the divine architect and
engineer of the universe. It is a day to honor our tools, machines, and
the craft that keeps our work running smoothly.

May this day bring you prosperity, smooth deployments, and zero downtime!

Warm regards,
{SENDER_NAME}
{SENDER_TITLE}
"""

HTML_BODY = f"""\
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width:600px; margin:auto; border:1px solid #eee;
                border-radius:8px; padding:24px;">
      <div style="text-align:center;">
        <img src="cid:{GEAR_CID}" width="90" height="90" alt="Spinning gear"
             style="display:inline-block;">
      </div>
      <h2 style="color:#d35400; text-align:center;">🙏 Happy Vishwakarma Puja!</h2>
      <p>Dear Friend,</p>
      <p>Wishing you a very <b>Happy Vishwakarma Puja</b>!</p>
      <p>
        Today, <b>{TODAY}</b>, we celebrate Lord Vishwakarma, the divine
        architect and engineer of the universe — a day to honor our tools,
        machines, and the craft that keeps our work running smoothly.
      </p>
      <p>May this day bring you prosperity, smooth deployments, and zero downtime!</p>
      <br>
      <p>
        Warm regards,<br>
        <b>{SENDER_NAME}</b><br>
        {SENDER_TITLE}
      </p>
    </div>
  </body>
</html>
"""


def build_message(to_addr: str, gear_gif_bytes: bytes) -> MIMEMultipart:
    # "related" wraps the alternative text/html part plus the inline image,
    # which is what lets the HTML reference the GIF via cid:GEAR_CID.
    msg = MIMEMultipart("related")
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = to_addr
    msg["Subject"] = SUBJECT

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(PLAIN_BODY, "plain"))
    alt.attach(MIMEText(HTML_BODY, "html"))
    msg.attach(alt)

    image = MIMEImage(gear_gif_bytes, _subtype="gif")
    image.add_header("Content-ID", f"<{GEAR_CID}>")
    image.add_header("Content-Disposition", "inline", filename="gear.gif")
    msg.attach(image)

    return msg


def send_emails():
    gear_gif_bytes = build_gear_gif()  # generate the animation once, reuse for everyone

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for recipient in RECIPIENTS:
            try:
                msg = build_message(recipient, gear_gif_bytes)
                server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
                print(f"✅ Sent to {recipient}")
            except Exception as e:
                print(f"❌ Failed to send to {recipient}: {e}")


if __name__ == "__main__":
    send_emails()