from __future__ import annotations


def split_frame_range(start: int, end: int, parts: int) -> list[list[int]]:
    if start > end:
        raise ValueError("start must be <= end")
    if parts <= 0:
        raise ValueError("parts must be > 0")

    frames = list(range(start, end + 1))
    parts = min(parts, len(frames))
    base = len(frames) // parts
    remainder = len(frames) % parts

    chunks: list[list[int]] = []
    cursor = 0
    for index in range(parts):
        size = base + (1 if index < remainder else 0)
        chunks.append(frames[cursor:cursor + size])
        cursor += size
    return chunks
