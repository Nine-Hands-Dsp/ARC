"""Rasterisation SVG -> RGBA (Chromium / Playwright), fond transparent."""
import numpy as np, io
from PIL import Image
from playwright.sync_api import sync_playwright

def raster(svg_text, w, h, scale=1.0):
    html = f"""<html><body style="margin:0;background:transparent">
    <div style="width:{w}px;height:{h}px">{svg_text}</div></body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=scale)
        pg.set_content(html)
        png = pg.screenshot(omit_background=True, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        b.close()
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))
