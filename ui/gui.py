import sys
import os
import json
import cv2
import shutil
import glob
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QCheckBox, QMessageBox, QRadioButton, QFileDialog, QTextEdit, QButtonGroup, QFrame
)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from backend.auth import signup_user, login_user, save_user_profile
from backend.posting_automation import generate_ai_image
from backend.instagram_verification import verify_instagram_username

# Import Instabot for Instagram personal posting
from instabot import Bot

REMEMBER_PATH = "remember_me.json"

# Modern Theme
light_theme = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fdfbfb, stop:1 #ebedee);
    color: #2c2c2c;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
QFrame#card {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 18px;
    padding: 28px;
    margin: 30px auto;
    max-width: 420px;
    backdrop-filter: blur(12px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.15);
}
QLabel {
    font-size: 15px;
    margin-bottom: 8px;
    font-weight: 600;
    color: #333;
}
QLineEdit, QTextEdit {
    font-size: 14px;
    border: 2px solid #e6e9f0;
    border-radius: 12px;
    padding: 10px 14px;
    background-color: #fafbfc;
    min-width: 220px;
    margin-bottom: 14px;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #4facfe;
    background: #fff;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4facfe, stop:1 #00f2fe);
    color: white;
    font-size: 15px;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 18px;
    margin-top: 18px;
    min-width: 120px;
    transition: all 0.25s ease;
    box-shadow: 0 6px 14px rgba(79,172,254,0.35);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f2fe, stop:1 #4facfe);
    transform: scale(1.04);
}
QCheckBox, QRadioButton {
    font-size: 14px;
    margin-bottom: 12px;
    color: #444;
}
QLabel[role="status"] {
    font-size: 13px;
    margin-top: 10px;
    color: #0072ff;
    font-weight: 600;
}
"""

dark_theme = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #141e30, stop:1 #243b55);
    color: #f5f5f5;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
QFrame#card {
    background: rgba(30,30,30,0.85);
    border-radius: 18px;
    padding: 28px;
    margin: 30px auto;
    max-width: 420px;
    backdrop-filter: blur(14px);
    box-shadow: 0 14px 28px rgba(0,0,0,0.45);
}
QLabel {
    font-size: 15px;
    margin-bottom: 8px;
    font-weight: 600;
    color: #eee;
}
QLineEdit, QTextEdit {
    font-size: 14px;
    border: 2px solid #444;
    border-radius: 12px;
    padding: 10px 14px;
    background-color: rgba(20,20,20,0.9);
    color: #f5f5f5;
    min-width: 220px;
    margin-bottom: 14px;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #00c6ff;
    background: #262626;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00c6ff, stop:1 #0072ff);
    color: white;
    font-size: 15px;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 18px;
    margin-top: 18px;
    min-width: 120px;
    transition: all 0.25s ease;
    box-shadow: 0 6px 16px rgba(0,198,255,0.4);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0072ff, stop:1 #00c6ff);
    transform: scale(1.04);
}
QCheckBox, QRadioButton {
    font-size: 14px;
    margin-bottom: 12px;
    color: #ddd;
}
QLabel[role="status"] {
    font-size: 13px;
    margin-top: 10px;
    color: #00c6ff;
    font-weight: 600;
}
"""

# Remember-me helpers
def save_remember(email, password):
    with open(REMEMBER_PATH, "w") as f:
        json.dump({"email": email, "password": password}, f)

def load_remember():
    try:
        with open(REMEMBER_PATH, "r") as f:
            data = json.load(f)
        return data.get("email", ""), data.get("password", "")
    except Exception:
        return "", ""

def clear_remember():
    try:
        os.remove(REMEMBER_PATH)
    except Exception:
        pass

# ---------------- Authentication Window ----------------
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instagram Poster - Signup/Login")
        self.resize(500, 420)
        self.setStyleSheet(light_theme) 
        self.current_theme = "light"

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(320)
        card.setMaximumWidth(375)
        card_layout = QVBoxLayout(card)
        
        self.theme_checkbox = QCheckBox("Dark Theme")
        self.theme_checkbox.stateChanged.connect(self.toggle_theme)
        card_layout.addWidget(self.theme_checkbox)

        self.email_label = QLabel("Email Address")
        card_layout.addWidget(self.email_label)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        card_layout.addWidget(self.email_input)

        self.password_label = QLabel("Password")
        card_layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        card_layout.addWidget(self.password_input)

        self.remember_checkbox = QCheckBox("Remember Me")
        card_layout.addWidget(self.remember_checkbox)

        btn_layout = QHBoxLayout()
        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.clicked.connect(self.signup)
        btn_layout.addWidget(self.signup_btn)
        self.login_btn = QPushButton("Log In")
        self.login_btn.clicked.connect(self.login)
        btn_layout.addWidget(self.login_btn)
        card_layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setProperty("role", "status")
        self.status_label.setWordWrap(True)
        card_layout.addWidget(self.status_label)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

        email, password = load_remember()
        if email:
            self.email_input.setText(email)
            self.password_input.setText(password)
            self.remember_checkbox.setChecked(True)

    def toggle_theme(self, state):
        if state == Qt.Checked:
            self.setStyleSheet(light_theme)
            self.setStyleSheet(dark_theme)  # placeholder for dark theme
        else:
            self.setStyleSheet(light_theme)
        self.current_theme = "light"

    def signup(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        try:
            user = signup_user(email, password)
            self.status_label.setText("✅ Signup successful! Please log in.")
            if self.remember_checkbox.isChecked():
                save_remember(email, password)
            else:
                clear_remember()
        except Exception as e:
            self.status_label.setText(f"❌ {str(e)}")

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        try:
            user = login_user(email, password)
            self.status_label.setText("✅ Login successful!")
            self.user = user
            if self.remember_checkbox.isChecked():
                save_remember(email, password)
            else:
                clear_remember()
            self.open_insta_username_window()
        except Exception as e:
            self.status_label.setText(f"❌ {str(e)}")

    def open_insta_username_window(self):
        self.hide()
        self.insta_window = InstagramUsernameWindow(self.user)
        self.insta_window.show()

# ---------------- Instagram Username Verification ----------------
class InstagramUsernameWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Instagram Username Verification")
        self.resize(460, 220)
        self.user = user
        self.setStyleSheet(light_theme)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(320)
        card.setMaximumWidth(375)
        card_layout = QVBoxLayout(card)

        label = QLabel("Enter your Instagram username:")
        card_layout.addWidget(label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Instagram username")
        card_layout.addWidget(self.username_input)

        btn_layout = QHBoxLayout()
        verify_btn = QPushButton("Verify & Continue")
        verify_btn.clicked.connect(self.verify_and_save)
        btn_layout.addWidget(verify_btn)
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        btn_layout.addWidget(logout_btn)
        card_layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        card_layout.addWidget(self.status_label)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def verify_and_save(self):
        username = self.username_input.text().strip()
        if not username:
            self.status_label.setText("❌ Please enter a username.")
            return
        try:
            verified = verify_instagram_username(username)
            if verified:
                save_user_profile(self.user['localId'], self.user['email'], username)
                self.status_label.setText("✅ Username verified and saved!")
                QMessageBox.information(self, "Success", "Instagram username verified and saved!")
                self.close()
                self.media_window = MediaUploadWindow(self.user)
                self.media_window.show()
            else:
                self.status_label.setText("❌ Instagram username does not exist.")
        except Exception as e:
            self.status_label.setText(f"❌ {str(e)}")

    def logout(self):
        clear_remember()
        self.close()
        self.auth_window = AuthWindow()
        self.auth_window.show()

# ---------------- Media Upload Window ----------------
class MediaUploadWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Instagram Story/Reel Upload")
        self.resize(560, 490)
        self.user = user
        self.selected_file = None
        self.generated_image_paths = []
        self.setStyleSheet(light_theme)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(320)
        card.setMaximumWidth(420)
        card_layout = QVBoxLayout(card)

        type_label = QLabel("Select media type to upload:")
        card_layout.addWidget(type_label)
        self.story_radio = QRadioButton("Story (Image/Video)")
        self.reel_radio = QRadioButton("Reel (Video only, max 15 sec)")
        self.story_radio.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_group = QButtonGroup(self)
        radio_group.addButton(self.story_radio)
        radio_group.addButton(self.reel_radio)
        radio_layout.addWidget(self.story_radio)
        radio_layout.addWidget(self.reel_radio)
        card_layout.addLayout(radio_layout)

        self.upload_btn = QPushButton("Select Media File")
        self.upload_btn.clicked.connect(self.open_file_dialog)
        card_layout.addWidget(self.upload_btn)
        self.selected_file_label = QLabel("No file selected.")
        self.selected_file_label.setWordWrap(True)
        card_layout.addWidget(self.selected_file_label)

        # Instagram login fields
        self.insta_username_input = QLineEdit()
        self.insta_username_input.setPlaceholderText("Instagram Username")
        card_layout.addWidget(self.insta_username_input)
        self.insta_password_input = QLineEdit()
        self.insta_password_input.setPlaceholderText("Instagram Password")
        self.insta_password_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.insta_password_input)

        caption_label = QLabel("Enter your caption or prompt (for AI image):")
        card_layout.addWidget(caption_label)
        self.caption_text = QTextEdit()
        self.caption_text.setPlaceholderText("Write your caption here...")
        card_layout.addWidget(self.caption_text)

        # Generate Image Button and Previews
        self.generate_btn = QPushButton("Generate Image")
        self.generate_btn.clicked.connect(self.generate_image)
        card_layout.addWidget(self.generate_btn)
        # New: horizontal layout for image previews
        self.image_preview_layout = QHBoxLayout()
        self.image_preview_widget = QWidget()
        self.image_preview_widget.setLayout(self.image_preview_layout)
        card_layout.addWidget(self.image_preview_widget)

        btn_layout = QHBoxLayout()
        self.post_btn = QPushButton("Post to Instagram")
        self.post_btn.clicked.connect(self.post_media)
        btn_layout.addWidget(self.post_btn)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        btn_layout.addWidget(self.logout_btn)
        card_layout.addLayout(btn_layout)
        card_layout.addStretch()
        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def open_file_dialog(self):
        if self.story_radio.isChecked():
            file_filter = "Media Files (*.png *.jpg *.jpeg *.mp4 *.mov *.avi)"
        else:
            file_filter = "Video Files (*.mp4 *.mov *.avi)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Media File", "", file_filter)
        if file_path:
            if self.reel_radio.isChecked():
                if not self.validate_video_length(file_path):
                    QMessageBox.warning(self, "Error", "Video exceeds 15 seconds max length for Reels.")
                    return
            self.selected_file = file_path
            self.selected_file_label.setText(f"Selected file: {os.path.basename(file_path)}")
            self.generated_image_paths = []
            self.clear_previews()

    def validate_video_length(self, file_path):
        try:
            cap = cv2.VideoCapture(file_path)
            duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            return duration <= 15
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read video length: {e}")
            return False

    def clear_previews(self):
        # Remove all image preview widgets
        while self.image_preview_layout.count():
            child = self.image_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def generate_image(self):
        caption = self.caption_text.toPlainText().strip()
        if not caption:
            QMessageBox.warning(self, "Error", "Please enter a prompt or caption first!")
            return
        try:
            self.clear_previews()
            self.generated_image_paths = []
            # Replicate call, gets ALL generated images (usually 1, sometimes more)
            image_paths = []
            output = generate_ai_image(caption)  # Make sure your function supports multi!
            for i, image_path in enumerate(output):
                img_label = QLabel()
                img_label.setCursor(QCursor(Qt.PointingHandCursor))
                pixmap = QPixmap(image_path).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(pixmap)
                img_label.setToolTip(f"Click to select image {i+1}")
                # Mark which is selected by setting border/style
                img_label.mousePressEvent = lambda _, p=image_path: self.select_generated_image(p)
                self.image_preview_layout.addWidget(img_label)
                image_paths.append(image_path)
            # Select the first image by default
            if image_paths:
                self.selected_file = image_paths[0]
                self.selected_file_label.setText("Generated image ready to post")
            self.generated_image_paths = image_paths
            if not image_paths:
                QMessageBox.warning(self, "Error", "No images generated!")
            else:
                QMessageBox.information(self, "Success", f"{len(image_paths)} image(s) generated! Click any to select.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate image: {e}")

    def select_generated_image(self, image_path):
        # Called when user clicks any preview to select it for posting
        self.selected_file = image_path
        self.selected_file_label.setText(f"Selected AI image: {os.path.basename(image_path)}")

    def post_media(self):
        caption = self.caption_text.toPlainText().strip()
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Please select a media file or generate an image first.")
            return
        insta_username = self.insta_username_input.text().strip()
        insta_password = self.insta_password_input.text().strip()
        if not insta_username or not insta_password:
            QMessageBox.warning(self, "Error", "Enter your Instagram username & password.")
            return
        try:
            config_path = os.path.join(os.getcwd(), "config")
            if os.path.exists(config_path):
                shutil.rmtree(config_path)
            for temp_file in glob.glob("*.REMOVE_ME"):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            bot = Bot()
            bot.login(username=insta_username, password=insta_password)
            # Handle upload type
            if self.selected_file.lower().endswith(('.mp4', '.mov', '.avi')):
                success = bot.upload_video(self.selected_file, caption=caption)
                if not success:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Instagram did not accept video format. Try converting video to MP4 (H.264) and keep under 15 seconds."
                    )
                    return
            else:
                success = bot.upload_photo(self.selected_file, caption=caption)
                if not success:
                    QMessageBox.warning(self, "Error", "Instagram did not accept the image.")
                    return
            bot.logout()
            for temp_file in glob.glob("*.REMOVE_ME"):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            QMessageBox.information(self, "Success", "Post uploaded to Instagram successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to post: {e}")

    def logout(self):
        clear_remember()
        self.close()
        self.auth_window = AuthWindow()
        self.auth_window.show()

# ... AuthWindow, InstagramUsernameWindow as before ...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())