from pathlib import Path

import pytest

from deja_platform_api.fotos.music.library import VivaroMusicLibrary


def test_lists_only_mp3_files(tmp_path: Path) -> None:
    (tmp_path / "primeira.mp3").write_bytes(b"music")
    (tmp_path / "segunda.MP3").write_bytes(b"music")
    (tmp_path / "imagem.jpg").write_bytes(b"image")
    (tmp_path / "documento.txt").write_text("text")

    library = VivaroMusicLibrary(tmp_path)

    assert library.list_tracks() == [
        "primeira.mp3",
        "segunda.MP3",
    ]


def test_missing_directory_returns_empty_list(tmp_path: Path) -> None:
    library = VivaroMusicLibrary(tmp_path / "inexistente")

    assert library.list_tracks() == []


def test_resolves_existing_track(tmp_path: Path) -> None:
    track = tmp_path / "musica.mp3"
    track.write_bytes(b"music")

    library = VivaroMusicLibrary(tmp_path)

    assert library.resolve_track("musica.mp3") == track.resolve()


@pytest.mark.parametrize(
    "filename",
    [
        "../segredo.mp3",
        "subpasta/musica.mp3",
        r"subpasta\musica.mp3",
        "imagem.jpg",
        "",
    ],
)
def test_rejects_invalid_track_names(
    tmp_path: Path,
    filename: str,
) -> None:
    library = VivaroMusicLibrary(tmp_path)

    with pytest.raises(ValueError):
        library.resolve_track(filename)


def test_rejects_missing_track(tmp_path: Path) -> None:
    library = VivaroMusicLibrary(tmp_path)

    with pytest.raises(FileNotFoundError):
        library.resolve_track("inexistente.mp3")


def test_rejects_symlink_outside_music_directory(
    tmp_path: Path,
) -> None:
    music_dir = tmp_path / "music"
    music_dir.mkdir()

    external_dir = tmp_path / "private"
    external_dir.mkdir()

    secret = external_dir / "segredo.mp3"
    secret.write_bytes(b"private")

    link = music_dir / "atalho.mp3"

    try:
        link.symlink_to(secret)
    except (OSError, NotImplementedError):
        pytest.skip("Links simbólicos indisponíveis neste ambiente.")

    library = VivaroMusicLibrary(music_dir)

    assert "atalho.mp3" not in library.list_tracks()

    with pytest.raises(FileNotFoundError):
        library.resolve_track("atalho.mp3")
