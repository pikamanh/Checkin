## Face Recognition Attendance System

This is a simple face recognition attendance system built using Python, PyQt6, OpenCV, and FaceTorch. It captures images from a webcam, performs face detection and recognition, and displays the recognized name.

## Features

- Real-time face recognition from a webcam feed.
- Saves captured frames to an image file for later reference.
- Displays the recognized name and similarity score on the GUI.
- Provides a "Warm Up" button to initialize the model for better performance.
- Allows users to start and stop the camera feed.

## Requirements

- Python 3.9+
- PyQt6
- OpenCV
- FaceTorch
- ImageIO
- Pandas

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/face-recognition-attendance.git
```

2. Install the required packages:

## Usage

1. Place the images of individuals you want to recognize in the `img` folder.
2. Run the `appVer2.py` file:

```bash
python appVer2.py
```

3. Click the "Warm Up" button to initialize the face recognition model.
4. Click the "Show" button to start the camera feed and begin face recognition.
5. The recognized name will be displayed in the text box on the GUI.
6. Click the "Break" button to stop the camera feed.

## Configuration

The application can be configured by modifying the parameters in the `appVer2.py` file:

- `folder`: Path to the folder containing the application files.
- `skip_frame_first`: Number of frames to skip at the beginning of the video stream.
- `frame_skip`: Number of frames to skip between predictions.
- `threshold`: Minimum similarity score for a positive match.

## Acknowledgments

- This project utilizes the FaceTorch library for face analysis.
- The GUI is built using PyQt6.

## Note

- The accuracy of the face recognition system may vary depending on factors such as lighting, image quality, and the training data used.
- It is recommended to use a diverse dataset of images for training the model to improve its accuracy.
- For optimal performance, ensure that the webcam is positioned correctly and the lighting conditions are favorable. 
