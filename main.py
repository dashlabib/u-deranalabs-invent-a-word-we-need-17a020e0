#!/usr/bin/env python3
"""Invent a Word We Need entry: showergument.

This program publishes one invented word with its one-line definition
to entry.txt in the output directory. It reads entry.txt next to this
file, runs the gate checks (UTF-8, 1-140 characters, not only
whitespace), and writes the exact bytes verbatim, verifying the
published file byte-for-byte against the source.

Standard library only. No network, no clock reads, no randomness:
fully deterministic.
"""

import argparse
import os
import sys
from pathlib import Path

SOURCE_PATH = Path(__file__).resolve().parent / "entry.txt"
DEFAULT_OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def gate_check(data: bytes):
    """Check the raw entry bytes against the gate. Return (text, errors)."""
    errors = []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, [f"not valid UTF-8: {exc}"]
    if not 1 <= len(text) <= 140:
        errors.append(f"length {len(text)} characters, must be 1-140")
    if not text.strip():
        errors.append("entry is only whitespace")
    # A single line: at most one trailing newline, no other line breaks.
    body = text[:-1] if text.endswith("\n") else text
    if "\n" in body or "\r" in text:
        errors.append("entry must be a single line")
    return text, errors


def gate_report(text: str) -> str:
    """Return a one-line summary of the gate result for an entry."""
    return (
        f"gate: valid, {len(text)} characters "
        f"({len(text.encode('utf-8'))} bytes), single line, UTF-8"
    )


def publish(output_dir: Path) -> str:
    """Publish entry.txt verbatim to output_dir and verify the copy."""
    data = SOURCE_PATH.read_bytes()
    text, errors = gate_check(data)
    if errors:
        raise ValueError("gate failed: " + "; ".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.txt"
    target.write_bytes(data)
    if target.read_bytes() != data:
        raise IOError("published entry.txt does not match source byte-for-byte")
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Publish the showergument entry.")
    parser.add_argument("--output-dir", default=None,
                        help="output directory (default: $MAKEFUN_OUTPUT_DIR or /output)")
    parser.add_argument("--verify-only", action="store_true",
                        help="check the source entry without writing anything")
    parser.add_argument("--show", action="store_true",
                        help="print the entry and its gate report")
    args = parser.parse_args(argv)

    if args.verify_only:
        data = SOURCE_PATH.read_bytes()
        text, errors = gate_check(data)
        if errors:
            print("gate failed: " + "; ".join(errors), file=sys.stderr)
            return 1
        print(text, end="" if text.endswith("\n") else "\n")
        print(gate_report(text))
        return 0

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    try:
        text = publish(output_dir)
    except (ValueError, IOError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.show:
        print(text, end="" if text.endswith("\n") else "\n")
        print(gate_report(text))
        print(f"published to {output_dir / 'entry.txt'}")
    else:
        # A plain run still leaves an auditable trace on stdout.
        print(gate_report(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
