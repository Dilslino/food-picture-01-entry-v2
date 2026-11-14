#!/usr/bin/env python3
"""Ship the bundled still image as this competition's entry.

The entry itself is one photograph, already finished.  This program
does not edit a single pixel: it sanity-checks the bundled JPEG and
then copies its bytes verbatim into the output folder under the name
entry.png.  Only the standard library is used, nothing is fetched
from the network, and the same input always yields the same output.
"""

import os
import sys


# Hard ceilings from the competition rules.
MAX_FILE_SIZE = 1024 * 1024
MAX_SIDE = 1024

JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"

# Markers whose segment carries a frame header.  DHT (0xC4), JPG (0xC8)
# and DAC (0xCC) are intentionally absent from this set.
FRAME_MARKERS = frozenset(
    [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
     0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]
)

# Markers with no length field at all, so a walker must never try to
# skip past them by reading a size.
LENGTHLESS = frozenset([0x01] + list(range(0xD0, 0xD8)))


def complain(text):
    """Report a problem on stderr and signal failure with exit code 1."""
    print("error: " + text, file=sys.stderr)
    return 1


def measure_frame(picture):
    """Walk JPEG segments and return (width, height) of the first frame.

    Returns None when no frame header is found before the scan data
    begins, or when any segment looks truncated or malformed.
    """
    cursor = 2  # the two SOI bytes have already been verified
    total = len(picture)
    while cursor + 1 < total:
        if picture[cursor] != 0xFF:
            cursor += 1
            continue
        code = picture[cursor + 1]
        if code == 0xFF:
            cursor += 1  # filler byte, not a real marker
            continue
        if code == 0x00:
            cursor += 2  # escaped 0xFF inside compressed data
            continue
        if code in LENGTHLESS:
            cursor += 2
            continue
        if code == 0xDA:
            return None  # start of scan: only entropy data follows
        if cursor + 4 > total:
            return None
        span = (picture[cursor + 2] << 8) | picture[cursor + 3]
        if span < 2 or cursor + 2 + span > total:
            return None
        if code in FRAME_MARKERS:
            payload = picture[cursor + 4:cursor + 2 + span]
            if len(payload) < 5:
                return None
            tall = (payload[1] << 8) | payload[2]
            wide = (payload[3] << 8) | payload[4]
            return wide, tall
        cursor += 2 + span
    return None


def run():
    folder = os.path.dirname(os.path.abspath(__file__))
    origin = os.path.join(folder, "image.jpg")
    try:
        with open(origin, "rb") as handle:
            picture = handle.read()
    except OSError as exc:
        return complain("cannot open image.jpg: %s" % exc)

    if len(picture) > MAX_FILE_SIZE:
        return complain("image.jpg is larger than 1 MiB")
    if len(picture) < 4:
        return complain("image.jpg is too short to be a JPEG")
    if not picture.startswith(JPEG_SOI):
        return complain("image.jpg does not start with a JPEG SOI marker")
    if not picture.endswith(JPEG_EOI):
        return complain("image.jpg does not end with a JPEG EOI marker")

    frame = measure_frame(picture)
    if frame is None:
        return complain("no frame header found inside image.jpg")
    wide, tall = frame
    if wide < 1 or tall < 1 or wide > MAX_SIDE or tall > MAX_SIDE:
        return complain("frame size %dx%d is outside the allowed range"
                        % (wide, tall))

    destination = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(destination, exist_ok=True)
        target = os.path.join(destination, "entry.png")
        with open(target, "wb") as handle:
            handle.write(picture)
    except OSError as exc:
        return complain("cannot write entry.png: %s" % exc)

    print("image.jpg -> entry.png: %dx%d, %d bytes" % (wide, tall, len(picture)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
