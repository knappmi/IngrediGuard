# IngrediGuard

A mobile application that helps users identify allergens in food products through menu scanning and ingredient analysis.

## Features

- **OCR Menu Scanning**: Capture and analyze restaurant menus using your phone's camera
- **Allergy Detection**: Identify potential allergens in food items based on your dietary restrictions
- **User-Friendly Interface**: Clean, intuitive design for easy navigation
- **Secure Authentication**: Protected user profiles and settings
- **Admin Dashboard**: Management tools for administrators

## Technology Stack

- **Framework**: Kivy (Python)
- **Platform**: Android (AAB/APK)
- **Database**: SQLite
- **OCR**: Integrated image processing
- **Architecture**: Clean separation of concerns with dedicated screens and utilities

## Project Structure

```text
IngrediGuard/
├── screens/           # UI screens and navigation
├── models/           # Data models and database
├── utils/            # Utility functions (OCR, filtering, etc.)
├── data/             # Assets and resources
├── tests/            # Unit tests
└── telemetry/        # Analytics and monitoring
```

## Getting Started

### Prerequisites

- Python 3.8+
- Buildozer for Android builds
- Android SDK and NDK (for local builds)

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. For Android builds: `buildozer android debug`

## Building for Production

The project includes GitHub Actions workflows for automated building:

- **Debug APK**: Built on feature branches
- **Release AAB**: Built on main branch for Play Store deployment

## License

This project is licensed under the MIT License.