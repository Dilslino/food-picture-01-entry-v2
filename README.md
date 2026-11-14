# food-picture-01 — Entry V2: "Midnight Tonkotsu: The Golden Lift"

Entry for the make.fun **food-picture-01** bounty (best-looking food
picture, pairwise judge, top 100 paid).

## Image

Steaming tonkotsu ramen in a speckled blue-grey ceramic bowl, 45-degree
three-quarter view: wooden chopsticks lifting a tall tangle of glossy
wavy noodles, molten ajitama yolk dripping, black-garlic oil (mayu)
swirl, glistening chashu, upright nori, scallions, chili oil droplets,
thick steam, dark moody table with warm golden-hour side light.

`image.jpg` — 1024x1024 JPEG, 212,561 bytes.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only) validates the image
against the gate (whole JPEG, at most 1 MiB, at most 1024x1024) and
copies it byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output`).

## License

MIT — see `LICENSE`.
