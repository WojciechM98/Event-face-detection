# Event face detection
A Python-based app for face detecting events on a image. Detected faces with metadata are stored in SQLite database. Using Flask to display data in HTML pages makes data management easier.

## How does this app works
Event face detection contains:
 - FaceExtractor module for face detection end extraction,
 - Main.py with Flask server and SQLite database.

### FaceExtraction module
This module contains FaceExtraction class which has two function for capture the image with faces init using MTCNN detector and extracting faces with given boundary box.

### Main.py
Main function where Flask server and SQLite using SQLAlchemy library is setup.
SQL dataset has two tables. First table called **Data** is set as a parent talbe. Each row contains 3 columns: **id**, **date**, **date_time**. Second table called **Images** is a child table and it inherits id from Data table. Each row contains 2 columns: **data_id** and **image**.

```
@app.route("/send-email/<int:image_id>")
def email_notification(image_id):
    send_email(image_id)
    return redirect(url_for('home'))
```
