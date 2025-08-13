from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
from Unifi.drivers.camera_driver import CameraDriver

class NullDriver(CameraDriver):
    async def get_snapshot_jpeg(self, timeout_s: int = 3) -> bytes:
        w, h = 1280, 720
        img = Image.new("RGB", (w, h), (32, 32, 32))
        d = ImageDraw.Draw(img)

        # Color bars (top half)
        bars = [(255,255,255),(255,255,0),(0,255,255),(0,255,0),(255,0,255),(255,0,0),(0,0,255)]
        bw = w // len(bars)
        for i, c in enumerate(bars):
            d.rectangle([i*bw, 0, (i+1)*bw, h//2], fill=c)

        # Grid (bottom half)
        for x in range(0, w, 80):
            d.line([(x, h//2), (x, h)], fill=(60,60,60))
        for y in range(h//2, h, 80):
            d.line([(0, y), (w, y)], fill=(60,60,60))

        # Label with timestamp
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = (self.settings.get("name") or "NullCam")
        text = f"{name}  {ts}  {w}x{h}"
        font = ImageFont.load_default()
        bbox = d.textbbox((0, 0), text, font=font)
        pad = 10
        box = (10, h//2 + 10, 10 + (bbox[2]-bbox[0]) + 2*pad, h//2 + 10 + (bbox[3]-bbox[1]) + 2*pad)
        d.rectangle(box, fill=(0,0,0))
        d.text((box[0]+pad, box[1]+pad), text, fill=(255,255,255), font=font)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        return buf.getvalue()