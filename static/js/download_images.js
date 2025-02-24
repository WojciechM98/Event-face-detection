console.log('Script is running');
var dateAndTimeElement = document.getElementById('dateAndTime');
var imgDate = dateAndTimeElement.getAttribute('data-img-date');
var imgTime = dateAndTimeElement.getAttribute('data-img-time');

// Function to create a zip archive and trigger download
function saveImages() {
    var zip = new JSZip();

    // Iterate over the base64 images and add them to the zip archive
    base64Images.forEach(function(base64Image, index) {
        zip.file(imgDate + '_' + imgTime + '_' + index + '.png', base64Image, { base64: true });
    });

    // Generate the zip archive
    zip.generateAsync({ type: 'blob' }).then(function(content) {
        // Create a temporary anchor element for downloading
        var a = document.createElement('a');
        a.href = URL.createObjectURL(content);
        a.download = 'images.zip'; // Set the desired zip file name
        a.style.display = 'none';

        // Trigger a click event on the anchor element to initiate the download
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
}

// Add click event listener to the "Save Images" button
document.getElementById('saveButton').addEventListener('click', saveImages);