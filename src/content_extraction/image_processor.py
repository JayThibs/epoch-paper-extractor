import os
from PIL import Image

class ImageProcessor:
    @staticmethod
    def save_images(images, output_dir):
        image_paths = []
        for i, (page_num, img) in enumerate(images):
            if not isinstance(img, Image.Image):
                img = Image.open(img) if isinstance(img, str) else Image.fromarray(img)
            image_path = os.path.join(output_dir, f"image_{page_num}_{i}.png")
            img.save(image_path)
            image_paths.append((page_num, image_path))
        return image_paths