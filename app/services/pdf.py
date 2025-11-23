import os
from PIL import Image
from app.services.logger import Logger

class PDFService:
    """Handles File I/O and PDF generation."""
    
    def merge_images_to_pdf(self, doc_name: str, image_dir: str, output_dir: str, logger: Logger):
        logger.info(f"  [MERGING] Creating PDF for {doc_name}...")
        
        images = []
        if os.path.exists(image_dir):
            for f in os.listdir(image_dir):
                if f.endswith(".jpg"):
                    images.append(f)
        
        try:
            images.sort(key=lambda x: int(x.split('.')[0]))
        except ValueError:
            images.sort()

        if not images:
            logger.info(f"  [WARNING] No images found for {doc_name}. Skipping PDF creation.")
            return

        try:
            first_image_path = os.path.join(image_dir, images[0])
            first_image = Image.open(first_image_path).convert('RGB')
            
            other_images = []
            for img_file in images[1:]:
                img_path = os.path.join(image_dir, img_file)
                img = Image.open(img_path).convert('RGB')
                other_images.append(img)

            pdf_path = os.path.join(output_dir, f"{doc_name}.pdf")
            first_image.save(pdf_path, save_all=True, append_images=other_images)
            logger.info(f"  [SUCCESS] Created {pdf_path}")
            
        except Exception as e:
            logger.error(f"Failed to create PDF for {doc_name}: {e}")

    def cleanup_images(self, doc_dir: str, logger: Logger):
        try:
            logger.info(f"  [CLEANUP] Removing downloaded images...")
            for f in os.listdir(doc_dir):
                if f.endswith(".jpg"):
                    os.remove(os.path.join(doc_dir, f))
            os.rmdir(doc_dir)
            logger.info(f"  [CLEANUP] Cleanup complete.")
        except Exception as e:
            logger.info(f"  [WARNING] Could not clean up images: {e}")
