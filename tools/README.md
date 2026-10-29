# Profile asset generator

The artwork in `../assets` is generated, not hand-edited.

```bash
pip install fonttools brotli
python3 build.py     # writes ../assets/*.svg (dark, light and mobile variants)
python3 readme.py    # writes ../README.md
```

- Edit project text, stack items and colors in `build.py`; edit page copy and links in `readme.py`.
- Fonts are subset per SVG and embedded, so each image renders the same inside GitHub's `<img>`.
- Colors and type follow the portfolio's Spec Sheet design system.
