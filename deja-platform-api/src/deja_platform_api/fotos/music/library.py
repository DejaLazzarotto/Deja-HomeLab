"""Biblioteca de músicas do VIVARO."""

from pathlib import Path


class VivaroMusicLibrary:
    """Consulta arquivos MP3 de um diretório autorizado."""

    def __init__(self, music_dir: Path) -> None:
        self.music_dir = music_dir.resolve()

    def list_tracks(self) -> list[str]:
        """Lista apenas arquivos MP3 válidos da pasta musical."""

        if not self.music_dir.is_dir():
            return []

        return sorted(
            path.name
            for path in self.music_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".mp3"
            and path.resolve().parent == self.music_dir
        )

    def resolve_track(self, filename: str) -> Path:
        """Resolve uma faixa sem permitir acesso fora da pasta."""

        if (
            not filename
            or filename != Path(filename).name
            or "/" in filename
            or "\\" in filename
            or Path(filename).suffix.lower() != ".mp3"
        ):
            raise ValueError("Nome de música inválido.")

        path = (self.music_dir / filename).resolve()

        if (
            path.parent != self.music_dir
            or not path.is_file()
        ):
            raise FileNotFoundError("Música não encontrada.")

        return path
