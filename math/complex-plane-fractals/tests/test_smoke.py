"""Быстрые проверки того, что иллюстрации и PDF строятся на малом разрешении."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from complexplane import figures
from complexplane.cli import cli


@pytest.mark.parametrize("name", list(figures.ALL))
def test_every_figure_builds_at_low_resolution(tmp_path: Path, name):
    path = figures.ALL[name](tmp_path, 0.12)
    assert path.exists() and path.stat().st_size > 1000


def test_unknown_figure_name(tmp_path: Path):
    with pytest.raises(KeyError):
        figures.build(["nope"], tmp_path)


def test_gallery_pdf_builds(tmp_path: Path):
    pytest.importorskip("img2pdf")
    from complexplane import gallery

    out = gallery.build(tmp_path / "g.pdf", scale=0.1)
    data = out.read_bytes()
    assert data.startswith(b"%PDF")
    import re

    pages = len(re.findall(rb"/Type\s*/Page(?![s\w])", data))
    # обложка, три листа миниатюр и по странице на каждую раскраску
    assert pages == 1 + 3 + len(gallery.entries())


def test_cli_mandelbrot_and_julia(tmp_path: Path):
    runner = CliRunner()
    r = runner.invoke(cli, ["mandelbrot", "--size", "120", "--iters", "60", "--mode", "classic",
                            "--palette", "afmhot", "--out", str(tmp_path / "m.png")])
    assert r.exit_code == 0, r.output
    r = runner.invoke(cli, ["julia", "--size", "120", "--iters", "60", "--out", str(tmp_path / "j.png")])
    assert r.exit_code == 0, r.output
    r = runner.invoke(cli, ["newton", "--size", "120", "--out", str(tmp_path / "n.png")])
    assert r.exit_code == 0, r.output
    assert all((tmp_path / f).exists() for f in ("m.png", "j.png", "n.png"))


def test_cli_rejects_bad_complex():
    r = CliRunner().invoke(cli, ["mandelbrot", "--center", "abc"])
    assert r.exit_code != 0
