"""Detector frontal e comparador LBPH (OpenCV opcional).

Uma identificação automática nunca é confirmada sem revisão humana.
"""

from pathlib import Path

from PIL import Image


class FaceEngineUnavailable(RuntimeError):
    pass


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise FaceEngineUnavailable(
            'Instale a opção "faces" da API para analisar rostos automaticamente.'
        ) from exc
    if not hasattr(cv2, "face"):
        raise FaceEngineUnavailable("A instalação do OpenCV precisa incluir o módulo contrib.")
    return cv2


def detect(image_path: Path) -> list[tuple[float, float, float, float]]:
    cv2 = _cv2()
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError("Não foi possível abrir o derivado da mídia.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
    )
    if cascade.empty():
        raise FaceEngineUnavailable("O detector facial do OpenCV não está disponível.")
    height, width = gray.shape
    boxes = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(32, 32))
    return [
        (float(x / width), float(y / height), float(w / width), float(h / height))
        for x, y, w, h in boxes
    ]


def suggest(crop: Image.Image, references: list[tuple[str, Path]]) -> tuple[str, float] | None:
    """Compara uma face com referências do mesmo ambiente; distância menor é melhor."""
    if not references:
        return None
    cv2 = _cv2()
    import numpy as np

    images = []
    labels = []
    people = []
    for person_id, path in references:
        if not path.is_file():
            continue
        with Image.open(path) as image:
            images.append(np.asarray(image.convert("L").resize((128, 128))))
        labels.append(len(people))
        people.append(person_id)
    if not images:
        return None
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.asarray(labels, dtype=np.int32))
    label, distance = recognizer.predict(np.asarray(crop.convert("L").resize((128, 128))))
    # Limite conservador; nunca altera vínculo sem confirmação humana.
    if distance >= 55:
        return None
    return people[label], max(0.0, min(1.0, 1.0 - distance / 100.0))
