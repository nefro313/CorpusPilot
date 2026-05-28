"""Markdown-table detection used by the financial SQL-RAG path.

LlamaParse emits tables as GitHub-flavored markdown. We pull them out of
each parsed unit and return a flat list of cells (one per column per row)
which is then persisted into `document_table_rows`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Matches a markdown table block: header row, separator row, body rows.
_TABLE_BLOCK_RE = re.compile(
    r"((?:^\|[^\n]+\|\s*$\n)+)",
    re.MULTILINE,
)
_SEPARATOR_RE = re.compile(r"^\|\s*[:-]+\s*(\|\s*[:-]+\s*)+\|\s*$")


@dataclass(frozen=True)
class PreparedTableCell:
    table_index: int
    row_index: int
    column_name: str
    cell_value: str
    page_number: int | None
    section_title: str | None


def _split_row(line: str) -> list[str]:
    parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return parts


def _looks_like_table(block: str) -> bool:
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if len(lines) < 3:
        return False
    return _SEPARATOR_RE.match(lines[1].strip()) is not None


def _parse_block(
    block: str,
    table_index: int,
    page_number: int | None,
    section_title: str | None,
) -> list[PreparedTableCell]:
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not _looks_like_table("\n".join(lines)):
        return []
    header = _split_row(lines[0])
    body = lines[2:]
    cells: list[PreparedTableCell] = []
    for row_idx, raw_row in enumerate(body):
        row_values = _split_row(raw_row)
        for col_idx, value in enumerate(row_values):
            if col_idx >= len(header):
                break
            column_name = header[col_idx] or f"col_{col_idx}"
            value = value.strip()
            if not value:
                continue
            cells.append(
                PreparedTableCell(
                    table_index=table_index,
                    row_index=row_idx,
                    column_name=column_name[:255],
                    cell_value=value,
                    page_number=page_number,
                    section_title=section_title,
                )
            )
    return cells


def extract_table_cells(units: list[dict[str, Any]]) -> list[PreparedTableCell]:
    """Scan parsed units for markdown tables and flatten them to cells."""
    cells: list[PreparedTableCell] = []
    table_index = 0
    for unit in units:
        text = unit.get("text") or ""
        if "|" not in text:
            continue
        for match in _TABLE_BLOCK_RE.finditer(text):
            block = match.group(1)
            if not _looks_like_table(block):
                continue
            new_cells = _parse_block(
                block,
                table_index=table_index,
                page_number=unit.get("page_number"),
                section_title=None,
            )
            if new_cells:
                cells.extend(new_cells)
                table_index += 1
    return cells
