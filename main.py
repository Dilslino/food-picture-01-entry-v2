"""food-picture-01 entry V2 (Python 3.13, standard library only).

Image: "Midnight Tonkotsu: The Golden Lift" — steaming tonkotsu ramen,
45-degree three-quarter view, chopsticks lifting a tall tangle of glossy
noodles, molten ajitama yolk, black-garlic oil swirl, 1024x1024 JPEG.

The program copies the image held in this repository (image.jpg, beside
this file) to the output directory as entry.png. The gate accepts a whole
PNG or JPEG of at most 1 MiB and 1024 by 1024 pixels, and the judge sees
exactly the bytes copied, so the copy must be byte-for-byte identical.

Before copying, the program validates the source against the gate's own
limits (whole JPEG: SOI marker first, EOI marker last; at most 1 MiB;
at most 1024 by 1024 pixels) and refuses to write anything invalid,
so a bad image can never be silently submitted.

After copying, the program reads the written file back and compares its
bytes with the source, so a truncated or corrupted copy is caught here
instead of reaching the judge; a mismatch removes the bad output and
fails cleanly.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys

MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.jpg")


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) of a JPEG from its SOF0/SOF2 segment."""
    if len(data) < 2 or data[0:2] != b"\xff\xd8":
        raise ValueError("not a JPEG (missing SOI marker)")
    if data[-2:] != b"\xff\xd9":
        raise ValueError("not a whole JPEG (missing EOI marker)")
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG segment at offset %d" % i)
        marker = data[i + 1]
        # Standalone markers carry no length field.
        if marker in (0x01, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8):
            i += 2
            continue
        if i + 4 > len(data):
            raise ValueError("truncated JPEG segment")
        length = (data[i + 2] << 8) | data[i + 3]
        if marker in (0xC0, 0xC2):  # SOF0 / SOF2: precision, height, width
            if length < 7 or i + 9 > len(data):
                raise ValueError("truncated SOF segment")
            height = (data[i + 5] << 8) | data[i + 6]
            width = (data[i + 7] << 8) | data[i + 8]
            return width, height
        if marker == 0xDA:  # SOS: scan data follows; dimensions already read
            raise ValueError("no SOF segment before scan data")
        i += 2 + length
    raise ValueError("no SOF segment found")


def fail(message: str) -> None:
    print("error: %s" % message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(SOURCE):
        fail("source image not found: %s" % SOURCE)
    with open(SOURCE, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        fail("image is %d bytes, over the 1 MiB limit" % len(data))
    try:
        width, height = jpeg_dimensions(data)
    except ValueError as exc:
        fail("invalid image: %s" % exc)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail("image is %dx%d, over the 1024x1024 limit" % (width, height))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        fail("output path is a file, not a directory: %s" % out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, out_path)
    with open(out_path, "rb") as f:
        written = f.read()
    if written != data:
        try:
            os.remove(out_path)
        except OSError:
            pass
        fail("written output does not match the source image")


if __name__ == "__main__":
    main()
