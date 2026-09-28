"""Instala modelos oficiais da OpenCV Zoo com verificação SHA-256."""

import argparse
import hashlib
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

MODELS = {
    "face_detection_yunet_2023mar.onnx": (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
        "models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    ),
    "face_recognition_sface_2021dec.onnx": (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
        "models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
        "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
    ),
}


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def install(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name, (url, expected_hash) in MODELS.items():
        path = target / name
        if path.is_file() and checksum(path) == expected_hash:
            print(f"Verificado: {name}")
            continue
        temporary: Path | None = None
        try:
            with urlopen(url, timeout=90) as source, NamedTemporaryFile(
                dir=target, prefix=f".{name}.", delete=False
            ) as output:
                temporary = Path(output.name)
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    output.write(block)
            if checksum(temporary) != expected_hash:
                raise ValueError(f"Checksum inválido para {name}; arquivo descartado.")
            os.replace(temporary, path)
            print(f"Instalado e verificado: {name}")
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", type=Path,
        default=Path(__file__).resolve().parents[1] / "models" / "fotos",
    )
    arguments = parser.parse_args()
    install(arguments.target)
