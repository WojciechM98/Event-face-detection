from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from face_extractor import FaceExtractor
import cv2
import datetime
import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import numpy as np

# Load env variables
load_dotenv()
SENDER_EMAIL = os.getenv('EMAIL')
SENDER_PASSWORD = os.getenv('PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER')

app = Flask(__name__, static_url_path='/static')
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy()
db.init_app(app)

# Create FaceExtractor object
face_detection = FaceExtractor()


# Data table Configuration
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)
    images = db.relationship('Images', backref='id', cascade="save-update, merge, delete, delete-orphan")


# Images table Configuration
class Images(db.Model):
    __tablename__ = 'images'
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'), primary_key=True)
    image = db.Column(db.PickleType)


with app.app_context():
    db.create_all()


def img_to_base64(array_list: list[np.ndarray]) -> list[str]:
    """Function for encoding numpy.ndarray images to base64 format.
    Returns a list of base64 strings."""

    base64_list = []
    for image in array_list:
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        base64_list.append(image_base64)

    return base64_list


def send_email(image_id: str):
    """Function for sending emails with images attached using SMTP."""

    # Query database for metadata and images with given ID
    images = db.get_or_404(Images, image_id).image
    metadata = db.get_or_404(Data, image_id)
    base64_images = img_to_base64(images)
    # Create a message object
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = 'Someone was at your front door.'

    # Attach the text message
    message = f'On date {metadata.date} at {metadata.date_time} someone was at your door.'
    msg.attach(MIMEText(message, 'plain'))

    # Attach the base64-encoded images as a MIMEImage
    for i, base64_image in enumerate(base64_images, start=1):
        image_data = base64.b64decode(base64_image)
        image_mime = MIMEImage(image_data, _subtype='.jpg')
        image_mime.add_header('Content-Disposition', f'attachment; filename=Image_{i}.jpg')
        msg.attach(image_mime)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


def get_all_data():
    # Get all data from database
    result = db.session.execute(db.select(Data).order_by(Data.id))

    return result.scalars().all()


@app.route("/")
def home():
    return render_template("index.html", data=get_all_data())


@app.route("/show-image")
def show_image():
    # Get variables from page
    img_id = request.args.get('id')
    img_date = request.args.get('date')
    img_time = request.args.get('time')
    # Query database Images table for images with given id
    images_to_show = db.get_or_404(Images, img_id).image
    # Convert NumPy array of an image to base64 format
    base64_list = img_to_base64(images_to_show)

    return render_template("image.html", data={'img_date': img_date,
                                               'img_time': img_time}, images_base64=base64_list)


@app.route("/delete")
def delete():
    # Get variables from page
    img_id = request.args.get('id')
    # Query database Data table with given row id
    image_to_delete = db.get_or_404(Data, img_id)
    # Delete row and commit changes
    db.session.delete(image_to_delete)
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/rec")
def rec():
    # Get current date and time
    now = datetime.datetime.now()
    date = now.strftime('%d-%m-%Y')
    time = now.strftime('%H:%M:%S')
    # Create custom ID string with date and time
    id_string = now.strftime('%Y%m%d%H%M%S')
    # Create new row in database Data table
    new_record = Data(id=id_string, date=date, date_time=time)
    # Run function for detecting and extracts face from and image
    images = face_detection.capture()
    # Create test list of images
    # images = [cv2.imread('output_img_from_database.jpg'), cv2.imread('2.jpg')]
    # Append list of numpy arrays (extracted images) to existing row in Images table
    new_image = Images(image=images, data_id=id_string)
    # Add and commit changes into database
    db.session.add(new_record)
    db.session.add(new_image)
    db.session.commit()
    send_email(id_string)
    
    return redirect(url_for('home'))


# @app.route("/send-email/<int:image_id>")
# def email_notification(image_id):
#     send_email(image_id)
#     return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
