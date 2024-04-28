# Face recognition attendance system

## An attendance system based on the face as a metric

using cv techniques to register the employees and take the attendance

## Table of Contents

- [Face recognition attendance system](#face-recognition-attendance-system)
  - [An attendance system based on the face as a metric](#an-attendance-system-based-on-the-face-as-a-metric)
  - [Table of Contents](#table-of-contents)
  - [File structure](#file-structure)
    - [gui](#gui)
      - [StartPage](#startpage)
      - [RecordingPage](#recordingpage)
      - [adminPanel](#adminpanel)
    - [Utils](#utils)
      - [processing](#processing)
      - [facedb](#facedb)
      - [resetdb](#resetdb)
    - [database](#database)
  - [Usage](#usage)
  - [License](#license)

use `pip` or `pip3`  

```
pip install virtualenv
```

```
python<version> -m venv <virtual-environment-name>
```

in `mac  \ linux`

```source env/bin/activate```

in `windows` 

```
env/Scripts/activate.bat //In CMD
```

```
env/Scripts/Activate.ps1 //In Powershel
```


after activating your virtual environment, you can install the project requirements using pip. Navigate to the project directory and run the following command:

```bash
    pip install -r requirements.txt
``` 
## File structure

The app consists of three main folder `gui` , `utils` and `database` , an entry point file `main.py`

### gui
```
gui
├── __init__.py
├── adminpanelframe.py
├── appgui.py
├── recordingpageframe.py
└── startpageframe.py
```
The gui folder app contain three frames `adminPanelPage` , `recordingPag` and `startPage`

#### StartPage

It gives you the initial navigation buttons to the other frames

#### RecordingPage

This page has the main functionality of the app where a camera capture the faces and record the attendance in real time in the database

#### adminPanel

This page give the admin some management capabilities

- register new employee
- delete new employee
- export the days attendance
- export the day's attendance
- export an employee attendance

all this pages are used by the app `appgui.py`

<hr>

### Utils
```
utils
├── __init__.py
├── facesdb.py
├── processing.py
└── resetdb.py
```
the utils folder contains 3 files `facedb.py` ,`processing.py` and `resetdb.py`

#### processing

The data pipeline is designed to process frames of images and perform face recognition on the detected faces. It consists of several functions that handle different stages of the pipeline.

Pre-processing Functions:

`str_to_np_ndarray`: Converts a string representation of a list to a NumPy ndarray.
load_employees: Loads employees' information into a dictionary, including their ID, name, and embedding.

`np_ndarrray_to_str`: Converts a NumPy ndarray to a string representation.

<hr>

Face Recognition Functions:


`get_embeddings`: Extracts facial embeddings from a given frame using a specified model.

`compare_embeddings_cosine_similarity`: Compares two embedding vectors using the cosine similarity metric.

`recognize_face`: Recognizes a face by comparing its embedding to the embeddings of known employees.

`draw_rectangle`: Draws a rectangle around a face in a frame.

`process_frame`: Processes a frame of an image to recognize faces and return the frame with drawn rectangles around recognized faces.

The pipeline starts by loading the employees' information into a dictionary using the `load_employees` function. Each employee is represented by their ID, name, and embedding. The embeddings are converted from string representations to NumPy `ndarrays` using the `str_to_np_ndarray` function.

When a frame is passed to the `process_frame` function, it first extracts facial embeddings from the frame using the `get_embeddings` function. The embeddings are then compared to the embeddings of known employees using the `recognize_face` function. If a match is found with a similarity score above a specified threshold, a rectangle is drawn around the recognized face using the `draw_rectangle` function.

The processed frame with drawn rectangles around recognized faces is returned, along with a set of recognized employee IDs.

Overall, this data pipeline enables the recognition of faces in frames of images by comparing their embeddings to the embeddings of known employees.

#### facedb

contains the `SQL` queries using `SQLITE`

#### resetdb

it resets the database to start with a clean database

This file needs to run with high privilege 
`sudo python resetdb.py  "path\to\database"`

in `windows` you will need to `run as administrator`

### database
the folder where the database file lies
## Usage 

Run the `main.py` file

```
    python main.py
```

## License

[Specify the license under which your project is distributed.]
