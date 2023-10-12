# Event face detection
A Python-based app for face detecting events on a image. Detected faces with metadata are stored in SQLite database. Using Flask to display data in HTML pages makes data management easier.

## How does this app works
Event face detection contains:
 - face_extractor module for face detection end extraction,
 - Main.py with Flask server and SQLite database.

### face_extractor module
This module contains FaceExtraction class which has two function for capture the image with faces init using MTCNN detector and extracting faces with given boundary box.

### Main.py
Main function where Flask server and SQLite using SQLAlchemy library is setup.
SQL dataset has two tables. First table called **Data** is set as a parent talbe. Each row contains 3 columns: **id**, **date**, **date_time**. Second table called **Images** is a child table and it inherits id from Data table. Each row contains 2 columns: **data_id** and **image**.

## Flask app routes

### Home Route (/):
```python
@app.route("/")
def home():
    return render_template("index.html", data=get_all_data())
```
This is the root route of Flask application. It renders an HTML template called "index.html" and passes data obtained from database with get_all_data() function to the template.

### Show Image Route (/show-image)
```python
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
```
This route is used to display an images. It retrieves the id, date, and time variables from the request's query parameters. Then, it queries the Images table in the database for an image with the given id. After retrieving the images, it converts it from a NumPy array to a base64 format using img_to_base64() function. Finally, it renders an HTML template called "image.html," passing the image data and other variables to the template.

### Record Route (/rec):
```python
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
```
This route is responsible for capturing and storing a new face images in the databse. It first obtains the current date and time. It then generates a custom id_string using the current date and time. It creates a new row in the Data table with this id_string. It captures images using a function called face_detection.capture(), which comes from face_extractor module. The captured images are added to the Images table in the database, associated with the same id_string. After adding the data and images to the database, it sends an email with use of send_email() function and redirects the user to the home page.

### Delete Route (/delete):
```python
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
```
This route is used to delete a record from the database. It retrieves the id variable from the request's query parameters and uses it to query the Data table in the database for the corresponding record. After successfully retrieving the record, it deletes it and commits the changes to the database. It then redirects the user back to the home page.







