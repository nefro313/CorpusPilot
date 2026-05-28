from services.ingestion.parsing import (
    checksum_bytes,
    infer_title,
    normalize_text,
    resolve_mime,
)


def test_checksum_is_deterministic_and_hex() -> None:
    a = checksum_bytes(b"hello world")
    b = checksum_bytes(b"hello world")
    assert a == b
    assert len(a) == 64
    assert all(c in "0123456789abcdef" for c in a)


def test_checksum_changes_with_payload() -> None:
    assert checksum_bytes(b"a") != checksum_bytes(b"b")


def test_infer_title_normalises_separators_and_strips_extension() -> None:
    assert infer_title("annual-report_2024.pdf") == "annual report 2024"
    assert infer_title("") == ""


def test_normalize_text_collapses_whitespace_and_strips_nulls() -> None:
    raw = "Hello\x00 world\r\n\r\n\r\nfoo   bar"
    out = normalize_text(raw)
    assert "\x00" not in out
    assert "\r" not in out
    assert "foo bar" in out
    assert out.startswith("Hello")


def test_resolve_mime_prefers_explicit_supported_mime() -> None:
    assert resolve_mime("x.bin", "application/pdf") == "application/pdf"


def test_resolve_mime_falls_back_to_extension() -> None:
    assert (
        resolve_mime("doc.docx", None)
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert resolve_mime("slides.pptx", None) is not None
    assert resolve_mime("page.html", None) == "text/html"
    assert resolve_mime("notes.md", None) == "text/markdown"


def test_resolve_mime_returns_none_for_unsupported() -> None:
    assert resolve_mime("archive.zip", None) is None
    assert resolve_mime("image.png", "image/png") is None
