from __future__ import annotations


def write_matrix(ws, data, append: bool = False, row_start: int = 1, col_start: int = 1) -> None:
    if append:
        row_start += ws.max_row
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            ws.cell(row_index + row_start, col_index + col_start, value)
