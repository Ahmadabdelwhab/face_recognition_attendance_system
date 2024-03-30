import numpy as np
import cv2
from deepface import DeepFace
from typing import List, Tuple, Dict, Set,Any
import json

#### pre-processing functions ##############


def str_to_np_ndarray(s: str) -> np.ndarray:
    """
    Convert a string representation of a list to a NumPy ndarray.

    Args:
        s (str): The string representation of a list.

    Returns:
        np.ndarray: The NumPy ndarray representation of the list.

    Example:
        str_to_np_ndarray('[1, 2, 3]')
        array([1, 2, 3])
    """
    list_embedding = json.loads(s)
    embedding = np.array(list_embedding)
    return embedding


def load_employees(employees: Tuple[List[int | str]]) -> Dict[int, List[str | np.ndarray]]:
    """
    Load employees' information into a dictionary.

    Args:
        employees (Tuple[List[int|str]]): A tuple of lists containing employee information.
            Each list should contain the employee's ID, name, and string representation of their embedding.

    Returns:
        Dict[int, List[str|np.ndarray]]: A dictionary where the employee ID is the key and the value is a list
            containing the employee's name and embedding.

    """
    employees_dict = {}
    for employee in employees:
        id, name, str_embedding = employee
        embedding = str_to_np_ndarray(str_embedding)
        employees_dict[id] = [name, embedding]
    return employees_dict


def np_ndarrray_to_str(embedding: np.ndarray) -> str:
    """
    Convert a NumPy ndarray to a string representation.

    Args:
        embedding (np.ndarray): The NumPy ndarray to be converted.

    Returns:
        str: The string representation of the ndarray.
    """
    list_embedding = embedding.tolist()
    str_embedding = json.dumps(list_embedding)
    return str_embedding


############################################
#### face recognition functions ############
MODEL_NAME = "Facenet"
FACE_DETECTOR_FAST = "opencv"
FACE_DETECTOR_SLOW = "mtcnn"
FACE_NORMALIZER = "Facenet"
THRESHOLD = 0.8


def get_embeddings(frame: np.ndarray, model_name: str = MODEL_NAME, face_detector: str = FACE_DETECTOR_FAST, face_normalizer=FACE_NORMALIZER) -> List[Dict[str, Any]]:
    """
    Extracts facial embeddings from a given frame using a specified model.

    Args:
        frame (np.ndarray): The input frame containing faces.
        model_name (str, optional): The name of the model to use for embedding extraction. Defaults to MODEL_NAME.
        face_detector (str, optional): The face detection backend to use. Defaults to FACE_DETECTOR_FAST.
        face_normalizer (str, optional): The face normalization method to use. Defaults to FACE_NORMALIZER.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the processed embeddings, including the bounding box coordinates, the embedding array, and the confidence score.

    Raises:
        ValueError: If no face is found in the frame.
        Exception: If an error occurs during the embedding extraction process.
    """
    try:
        deep_face_embeddings = DeepFace.represent(frame,
                                                model_name=model_name,
                                                detector_backend=face_detector,
                                                normalization=face_normalizer)

        def process_embeddings(embedding: Dict[str, Any]) -> List[Dict[str, str | Tuple[int] | float| np.ndarray]]:
            processed_embeddings = {}
            processed_embeddings["box"] = (embedding["facial_area"]["x"], embedding["facial_area"]["y"], embedding["facial_area"]["w"], embedding["facial_area"]["h"])
            processed_embeddings["embedding"] = np.array(embedding["embedding"])
            processed_embeddings["confidence"] = embedding["face_confidence"]
            return processed_embeddings
        embeddings = [process_embeddings(embedding)for embedding in deep_face_embeddings]
    except ValueError as e:
        print("No Face Found")
        return None
    except Exception as e:
        raise e
    return embeddings


def compare_embeddings_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compare two embedding vectors using the cosine similarity metric.

    Args:
        embedding1 (np.ndarray): The first embedding vector.
        embedding2 (np.ndarray): The second embedding vector.

    Returns:
        float: The cosine similarity between the two embedding vectors.
    """
    similarity = np.dot(embedding1, embedding2) / \
        (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return similarity


def recognize_face(embedding: np.ndarray, employees: Dict[int, List[str | np.ndarray]], threshold: float = THRESHOLD) -> Tuple[int, str, float]:
    """
    Recognize a face by comparing its embedding to the embeddings of known employees.

    Args:
        embedding (np.ndarray): The embedding vector of the face to be recognized.
        employees (Dict[int, List[str|np.ndarray]]): A dictionary of known employees and their embeddings.
        threshold (float, optional): The minimum similarity score for a match to be considered valid. Defaults to 0.6.

    Returns:
        Tuple[int, str, float]: A tuple containing the ID, name, and similarity score of the recognized employee.
    """
    max_similarity = -1
    recognized_employee_id = -1
    for id, (name, employee_embedding) in employees.items():
        similarity = compare_embeddings_cosine_similarity(
            embedding, employee_embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            recognized_employee_id = id
            recognized_employee_name = name
    if max_similarity > threshold:
        return recognized_employee_id, recognized_employee_name, max_similarity
    else:
        return -1, "Unknown", max_similarity

def draw_rectangle(frame: np.ndarray, confidence, name, box: Tuple[int, int, int, int], color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2):
    """
    Draw a rectangle around a face in a frame.

    Args:
        frame (np.ndarray): The input frame containing the face.
        box (Tuple[int,int,int,int]): The bounding box coordinates of the face.
        color (Tuple[int,int,int], optional): The color of the rectangle. Defaults to (0,255,0).
        thickness (int, optional): The thickness of the rectangle. Defaults to 2.

    Returns:
        np.ndarray: The frame with the rectangle drawn around the face.
    """
    x, y, w, h = box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    cv2.putText(frame, name  +  F" , {confidence:.2f}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, thickness)
    return frame


def process_frame(frame: np.ndarray, employees: Dict[int, List[str | np.ndarray]]) -> Tuple[np.ndarray | Set[int]]:
    """
    Process a frame of an image to recognize faces and return the frame with drawn rectangles around recognized faces.

    Args:
        frame (np.ndarray): The input frame of an image.
        employees (Dict[int, List[str | np.ndarray]]): A dictionary containing employee IDs as keys and a list of their names and embeddings as values.

    Returns:
        Tuple[np.ndarray | Set[int]]: A tuple containing the processed frame with drawn rectangles around recognized faces and a set of recognized employee IDs.
    """
    set_of_ids = set()
    embeddings = get_embeddings(frame)
    if embeddings is None:
        return frame, None
    for embedding in embeddings:
        id, name, simlarity = recognize_face(embedding["embedding"], employees)
        if id != -1:
            set_of_ids.add(id)
        box_color = (0, int(255 * simlarity) , int(255 * (1-simlarity)))
        draw_rectangle(frame, simlarity, name, embedding["box"], color=box_color)
    return frame, set_of_ids

