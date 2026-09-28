"""Detecção YuNet e comparação SFace; sugestões sempre exigem revisão humana."""

from pathlib import Path

from PIL import Image

DETECTOR_FILE = "face_detection_yunet_2023mar.onnx"
RECOGNIZER_FILE = "face_recognition_sface_2021dec.onnx"
MIN_SIMILARITY = 0.50
MIN_MARGIN = 0.08


class FaceEngineUnavailable(RuntimeError):
    pass


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise FaceEngineUnavailable(
            'Instale a opção "faces" da API para analisar rostos automaticamente.'
        ) from exc
    if not hasattr(cv2, "FaceDetectorYN") or not hasattr(cv2, "FaceRecognizerSF"):
        raise FaceEngineUnavailable("Atualize o OpenCV para usar YuNet e SFace.")
    return cv2


def check_models(models_dir: Path) -> tuple[Path, Path]:
    detector = models_dir / DETECTOR_FILE
    recognizer = models_dir / RECOGNIZER_FILE
    if not detector.is_file() or not recognizer.is_file():
        raise FaceEngineUnavailable(
            "Instale os modelos faciais com python scripts/install_fotos_face_models.py."
        )
    return detector, recognizer


def _detector(cv2, model: Path, width: int, height: int, *, threshold: float = 0.85):
    return cv2.FaceDetectorYN.create(
        str(model), "", (width, height), score_threshold=threshold
    )


def detect(
    image_path: Path, models_dir: Path = Path("models/fotos")
) -> list[tuple[float, float, float, float]]:
    cv2 = _cv2()
    detector_path, _ = check_models(models_dir)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError("Não foi possível abrir o derivado da mídia.")
    original_height, original_width = image.shape[:2]
    scale = min(1.0, 1200 / max(original_width, original_height))
    if scale < 1:
        image = cv2.resize(
            image,
            (round(original_width * scale), round(original_height * scale)),
        )
    height, width = image.shape[:2]
    try:
        _, faces = _detector(cv2, detector_path, width, height).detect(image)
        if faces is None:
            _, faces = _detector(
                cv2, detector_path, width, height, threshold=0.70
            ).detect(image)
    except cv2.error as exc:
        raise FaceEngineUnavailable("Não foi possível carregar o detector facial.") from exc
    boxes = []
    for face in [] if faces is None else faces:
        x, y, box_width, box_height = face[:4]
        left, top = max(0.0, float(x)), max(0.0, float(y))
        right = min(float(width), float(x + box_width))
        bottom = min(float(height), float(y + box_height))
        if right - left >= 32 and bottom - top >= 32:
            boxes.append((left / width, top / height, (right - left) / width,
                          (bottom - top) / height))
    return boxes


def _feature(crop: Image.Image, cv2, detector_path: Path, recognizer):
    import numpy as np

    image = cv2.cvtColor(np.asarray(crop.convert("RGB")), cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]
    if min(width, height) < 32:
        return None
    detector = _detector(cv2, detector_path, width, height, threshold=0.80)
    _, faces = detector.detect(image)
    if faces is None or not len(faces):
        return None
    face = max(faces, key=lambda row: float(row[2] * row[3] * row[-1]))
    return recognizer.feature(recognizer.alignCrop(image, face))


def validate_reference(crop: Image.Image, models_dir: Path) -> bool:
    cv2 = _cv2()
    detector_path, recognizer_path = check_models(models_dir)
    try:
        recognizer = cv2.FaceRecognizerSF.create(str(recognizer_path), "")
        return _feature(crop, cv2, detector_path, recognizer) is not None
    except cv2.error as exc:
        raise FaceEngineUnavailable("Não foi possível carregar os modelos faciais.") from exc


def _best_match(candidate, references, cv2, detector_path, recognizer):
    scores: dict[str, float] = {}
    for person_id, path in references:
        if not path.is_file():
            continue
        with Image.open(path) as image:
            known = _feature(image, cv2, detector_path, recognizer)
        if known is None:
            continue
        score = float(recognizer.match(candidate, known, cv2.FaceRecognizerSF_FR_COSINE))
        scores[person_id] = max(scores.get(person_id, -1.0), score)
    if not scores:
        return None
    ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    person_id, score = ranking[0]
    if score < MIN_SIMILARITY or (len(ranking) > 1 and score - ranking[1][1] < MIN_MARGIN):
        return None
    return person_id, max(0.0, min(1.0, score))


def suggest(
    crop: Image.Image,
    references: list[tuple[str, Path]],
    models_dir: Path = Path("models/fotos"),
) -> tuple[str, float] | None:
    """Retorna uma sugestão conservadora por similaridade cosseno, nunca confirma."""
    if not references:
        return None
    cv2 = _cv2()
    detector_path, recognizer_path = check_models(models_dir)
    try:
        recognizer = cv2.FaceRecognizerSF.create(str(recognizer_path), "")
        candidate = _feature(crop, cv2, detector_path, recognizer)
        if candidate is None:
            return None
        return _best_match(candidate, references, cv2, detector_path, recognizer)
    except (cv2.error, OSError, ValueError) as exc:
        raise FaceEngineUnavailable("Não foi possível comparar os rostos.") from exc


def suggest_in_image(
    image_path: Path,
    box: tuple[float, float, float, float],
    references: list[tuple[str, Path]],
    models_dir: Path = Path("models/fotos"),
) -> tuple[str, float] | None:
    """Compara um rosto detectado sem perdê-lo ao recortar a imagem."""
    if not references:
        return None
    cv2 = _cv2()
    detector_path, recognizer_path = check_models(models_dir)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError("Não foi possível abrir o derivado da mídia.")
    height, width = image.shape[:2]
    scale = min(1.0, 1200 / max(width, height))
    if scale < 1:
        image = cv2.resize(image, (round(width * scale), round(height * scale)))
    height, width = image.shape[:2]
    try:
        _, faces = _detector(cv2, detector_path, width, height, threshold=0.70).detect(image)
        if faces is None:
            return None
        x, y, w, h = box
        target = (x * width, y * height, (x + w) * width, (y + h) * height)
        best_face = None
        best_overlap = 0.0
        for face in faces:
            fx, fy, fw, fh = map(float, face[:4])
            left, top = max(0.0, fx), max(0.0, fy)
            right, bottom = min(float(width), fx + fw), min(float(height), fy + fh)
            intersection = max(0.0, min(target[2], right) - max(target[0], left)) * max(
                0.0, min(target[3], bottom) - max(target[1], top)
            )
            area = max(0.0, right - left) * max(0.0, bottom - top)
            overlap = intersection / min(w * width * h * height, area) if area else 0.0
            if overlap > best_overlap:
                best_face, best_overlap = face, overlap
        if best_face is None or best_overlap < 0.60:
            return None
        recognizer = cv2.FaceRecognizerSF.create(str(recognizer_path), "")
        candidate = recognizer.feature(recognizer.alignCrop(image, best_face))
        return _best_match(candidate, references, cv2, detector_path, recognizer)
    except (cv2.error, OSError, ValueError) as exc:
        raise FaceEngineUnavailable("Não foi possível comparar os rostos.") from exc
