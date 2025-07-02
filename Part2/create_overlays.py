import os
import numpy as np
from PIL import Image, ImageDraw

def create_directory():
    overlay_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlays')
    os.makedirs(overlay_dir, exist_ok=True)
    return overlay_dir

def create_sunglasses_overlay():
    width, height = 300, 100
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)


    draw.rectangle([(10, 40), (width-10, 60)], fill=(0, 0, 0, 255))


    draw.ellipse([(20, 20), (120, 80)], fill=(0, 0, 0, 200))


    draw.ellipse([(180, 20), (280, 80)], fill=(0, 0, 0, 200))


    draw.rectangle([(120, 40), (180, 60)], fill=(0, 0, 0, 255))

    return image

def create_hat_overlay():
    width, height = 300, 200
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)


    draw.rectangle([(20, 150), (width-20, 170)], fill=(139, 69, 19, 255))


    draw.rectangle([(60, 50), (width-60, 150)], fill=(165, 42, 42, 255))


    draw.rectangle([(60, 120), (width-60, 140)], fill=(0, 0, 0, 200))

    return image

def create_mustache_overlay():
    width, height = 200, 60
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))



    for i in range(width):
        for j in range(height):

            x_rel = (i - width/2) / (width/2)
            y_rel = (j - height/2) / (height/2)


            if abs(x_rel) < 0.8 and abs(y_rel) < 0.5:
                if abs(y_rel - 0.2 * np.sin(np.pi * x_rel)) < 0.2:

                    image.putpixel((i, j), (0, 0, 0, 200))

    return image

def save_overlays():
    overlay_dir = create_directory()


    sunglasses = create_sunglasses_overlay()
    sunglasses.save(os.path.join(overlay_dir, 'sunglasses.png'))


    hat = create_hat_overlay()
    hat.save(os.path.join(overlay_dir, 'hat.png'))


    mustache = create_mustache_overlay()
    mustache.save(os.path.join(overlay_dir, 'mustache.png'))

    print(f"Overlay images created in {overlay_dir}")

if __name__ == "__main__":
    save_overlays()
