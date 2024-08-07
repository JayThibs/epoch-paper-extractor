import cv2
import os

class ImageProcessor:
    @staticmethod
    def save_images(images, output_dir):
        image_paths = []
        for page_num, image in images:
            filename = f"image_page_{page_num}_{len(image_paths)}.png"
            path = os.path.join(output_dir, filename)
            cv2.imwrite(path, image)
            image_paths.append((page_num, path))
        return image_paths