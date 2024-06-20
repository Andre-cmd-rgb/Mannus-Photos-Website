import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage, firestore
from io import BytesIO
import uuid

# Firebase and Storage settings
FIREBASE_CREDENTIALS_PATH = "creds.json"
FIREBASE_STORAGE_BUCKET = 'gallery-891a6.appspot.com'
FIREBASE_COLLECTION = 'images'

# Initialize Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'storageBucket': FIREBASE_STORAGE_BUCKET
})
db = firestore.client()

class ImageUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.imagePath = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Uploader')
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        # Image display
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedSize(600, 400)
        self.layout.addWidget(self.imageLabel)

        # Button to open file dialog
        self.uploadButton = QPushButton('Select Image', self)
        self.uploadButton.clicked.connect(self.openFileDialog)
        self.layout.addWidget(self.uploadButton)

        # Title input
        self.titleLabel = QLabel('Title:', self)
        self.layout.addWidget(self.titleLabel)
        self.titleEdit = QLineEdit(self)
        self.layout.addWidget(self.titleEdit)

        # Description input
        self.descriptionLabel = QLabel('Description:', self)
        self.layout.addWidget(self.descriptionLabel)
        self.descriptionEdit = QTextEdit(self)
        self.layout.addWidget(self.descriptionEdit)

        # Button to upload image to Firebase
        self.uploadImageButton = QPushButton('Upload to Firebase', self)
        self.uploadImageButton.clicked.connect(self.uploadImageToFirebase)
        self.layout.addWidget(self.uploadImageButton)

        # Terminal for printing messages
        self.terminal = QTextEdit(self)
        self.terminal.setReadOnly(True)
        self.layout.addWidget(self.terminal)

        self.setLayout(self.layout)

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.gif)", options=options)
        if fileName:
            self.displayImage(fileName)
            self.imagePath = fileName
            self.printMessage(f"Selected image: {fileName}")

    def displayImage(self, file_path):
        pixmap = QPixmap(file_path)
        self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def createThumbnail(self, image_path, thumb_size=(150, 150)):
        with Image.open(image_path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail(thumb_size)
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            return buffer.getvalue()

    def uploadImageToFirebase(self):
        if not self.imagePath:
            self.showError("No image selected.")
            return

        image_id = str(uuid.uuid4())
        try:
            full_image_url = self.uploadImage(self.imagePath, image_id)
            thumbnail_url = self.uploadThumbnail(self.imagePath, image_id)

            # Add metadata to Firestore
            image_metadata = {
                'title': self.titleEdit.text(),
                'description': self.descriptionEdit.toPlainText(),
                'fullImageUrl': full_image_url,
                'thumbnailUrl': thumbnail_url,
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            db.collection(FIREBASE_COLLECTION).document(image_id).set(image_metadata)

            self.showMessage("Image uploaded successfully.")
            self.printMessage(f"Image uploaded successfully. Full Image URL: {full_image_url}, Thumbnail URL: {thumbnail_url}")
            self.clearUI()
        except Exception as e:
            self.showError(f"Failed to upload image: {str(e)}")
            self.printMessage(f"Failed to upload image: {str(e)}", isError=True)

    def uploadImage(self, image_path, image_id):
        bucket = storage.bucket()
        blob = bucket.blob(f'images/full/{image_id}.jpg')
        blob.upload_from_filename(image_path)
        blob.make_public()  # Make the blob publicly accessible
        return blob.public_url

    def uploadThumbnail(self, image_path, image_id):
        thumbnail_data = self.createThumbnail(image_path)
        bucket = storage.bucket()
        blob = bucket.blob(f'images/thumbs/{image_id}.jpg')
        blob.upload_from_string(thumbnail_data, content_type='image/jpeg')
        blob.make_public()  # Make the blob publicly accessible
        return blob.public_url

    def clearUI(self):
        self.imageLabel.clear()
        self.titleEdit.clear()
        self.descriptionEdit.clear()
        self.imagePath = None

    def showMessage(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("Success")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def showError(self, error):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(error)
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def printMessage(self, message, isError=False):
        if isError:
            self.terminal.append(f"<span style='color:red;'>{message}</span>")
        else:
            self.terminal.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageUploader()
    ex.show()
    sys.exit(app.exec_())
