# Identity Verification System

A Flask-based web application that provides identity and age verification services using Aadhar card document verification and facial recognition.

## Features

- **Document Processing**: OCR extraction of date of birth from Aadhar cards using Tesseract
- **Face Recognition**: Facial comparison between Aadhar photo and selfie using DeepFace
- **Age Verification**: Automatic age calculation and validation
- **Image Quality Validation**: Checks for blur, brightness, and other quality issues
- **Progressive Web Interface**: Step-by-step verification process with real-time camera integration

## Technology Stack

- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Database**: SQLite (default) with PostgreSQL support
- **Computer Vision**: OpenCV, DeepFace, and Tesseract OCR
- **Deployment**: Gunicorn WSGI server

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd identity-verification-system
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
export SESSION_SECRET="your-secret-key"
export DATABASE_URL="sqlite:///verification.db"  # Optional
```

4. Run the application:

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Start Verification**: Click "Start New Verification" to begin
2. **Upload Aadhar**: Upload a clear image of an Aadhar card
3. **Capture Selfie**: Use your camera to capture a selfie for face verification
4. **View Results**: Get comprehensive verification results including age validation

## System Requirements

- Python 3.11+
- Tesseract OCR
- Camera access for selfie capture
- Minimum 512MB RAM for TensorFlow operations

## Configuration

The application supports configuration through environment variables:

- `SESSION_SECRET`: Flask session secret key
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `TESSERACT_CMD`: Path to Tesseract executable

## Architecture

The application follows a traditional MVC pattern:

- **Models**: Database schemas in `models.py`
- **Views**: HTML templates in `templates/`
- **Controllers**: Route handlers in `routes.py`
- **Services**: Business logic in `verification_service.py`

## Security Considerations

- Secure file upload handling with size limits
- File type validation for uploaded images
- Session-based verification tracking
- No persistent storage of sensitive biometric data

## Sample Images

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**TensorFlow Import Errors**: Ensure NumPy version compatibility (1.26.4 recommended)

**Tesseract Not Found**: Install Tesseract OCR and set the correct path

**Camera Access Denied**: Enable camera permissions in your browser

**Large File Uploads**: Check the 16MB file size limit configuration

## Support

For support and questions, please open an issue in the GitHub repository.
