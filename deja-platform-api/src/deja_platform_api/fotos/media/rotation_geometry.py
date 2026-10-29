"""Transformações geométricas para rotação de fotografias."""

def rotate_face_box(
    x: float,
    y: float,
    width: float,
    height: float,
    degrees: int,
) -> tuple[float, float, float, float]:
    """Gira coordenadas normalizadas no sentido horário."""

    if degrees == 0:
        return x, y, width, height

    if degrees == 90:
        return (
            1.0 - y - height,
            x,
            height,
            width,
        )

    if degrees == 180:
        return (
            1.0 - x - width,
            1.0 - y - height,
            width,
            height,
        )

    if degrees == 270:
        return (
            y,
            1.0 - x - width,
            height,
            width,
        )

    raise ValueError(
        "A rotação deve ser 0, 90, 180 ou 270 graus."
    )


def rotation_delta(current_degrees: int, target_degrees: int) -> int:
    """Calcula a rotação adicional no sentido horário."""

    valid_angles = (0, 90, 180, 270)

    if current_degrees not in valid_angles:
        raise ValueError("Orientação atual inválida.")

    if target_degrees not in valid_angles:
        raise ValueError("Orientação desejada inválida.")

    return (target_degrees - current_degrees) % 360