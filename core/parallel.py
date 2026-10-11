from __future__ import annotations


def split_sequence(items, parts: int):
    if parts <= 0:
        raise ValueError("parts must be > 0")
    if not items:
        return []

    parts = min(parts, len(items))
    base = len(items) // parts
    remainder = len(items) % parts

    chunks = []
    cursor = 0
    for index in range(parts):
        size = base + (1 if index < remainder else 0)
        chunks.append(items[cursor:cursor + size])
        cursor += size
    return chunks
