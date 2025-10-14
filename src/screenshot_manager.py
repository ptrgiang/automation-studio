"""
Screenshot Manager for Automation Studio
Handles screen capture, thumbnail generation, and image storage
"""
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict
import pyautogui
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import logging


class ScreenshotManager:
    """Manages screenshot capture, storage, and thumbnail generation"""

    def __init__(self, base_dir: str = "screenshots"):
        """
        Initialize screenshot manager

        Args:
            base_dir: Base directory for storing screenshots
        """
        self.base_dir = Path(base_dir)
        self.screenshots_dir = self.base_dir / "full"
        self.thumbnails_dir = self.base_dir / "thumbnails"
        self.regions_dir = self.base_dir / "regions"

        # Create directories
        self._ensure_directories()

        # Counter for generating unique filenames
        self.counter = self._get_next_counter()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self.regions_dir.mkdir(parents=True, exist_ok=True)

    def _get_next_counter(self) -> int:
        """Get next available counter for unique filenames"""
        existing_files = list(self.screenshots_dir.glob("action_*.png"))
        if not existing_files:
            return 1

        # Extract numbers from filenames
        numbers = []
        for f in existing_files:
            try:
                num = int(f.stem.split('_')[1])
                numbers.append(num)
            except (IndexError, ValueError):
                pass

        return max(numbers, default=0) + 1

    def _generate_filename(self, prefix: str = "action") -> str:
        """Generate unique filename"""
        filename = f"{prefix}_{self.counter:04d}.png"
        self.counter += 1
        return filename

    def capture_full_screen(self, delay: float = 0.0) -> str:
        """
        Capture full screen

        Args:
            delay: Delay before capture in seconds

        Returns:
            Path to saved screenshot
        """
        if delay > 0:
            time.sleep(delay)

        try:
            # Capture screenshot
            screenshot = pyautogui.screenshot()

            # Save full screenshot
            filename = self._generate_filename()
            filepath = self.screenshots_dir / filename

            screenshot.save(str(filepath), 'PNG')
            logging.info(f"Full screen captured: {filepath}")

            return str(filepath)

        except Exception as e:
            logging.error(f"Error capturing screen: {str(e)}")
            return ""

    def capture_region(self, x: int, y: int, width: int, height: int,
                      delay: float = 0.0) -> Tuple[str, str]:
        """
        Capture specific screen region

        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            delay: Delay before capture in seconds

        Returns:
            Tuple of (full_screenshot_path, region_screenshot_path)
        """
        if delay > 0:
            time.sleep(delay)

        try:
            # Capture full screen first
            full_screenshot = pyautogui.screenshot()

            # Save full screenshot
            full_filename = self._generate_filename()
            full_filepath = self.screenshots_dir / full_filename
            full_screenshot.save(str(full_filepath), 'PNG')

            # Extract and save region
            region = full_screenshot.crop((x, y, x + width, y + height))
            region_filename = self._generate_filename("region")
            region_filepath = self.regions_dir / region_filename
            region.save(str(region_filepath), 'PNG')

            logging.info(f"Region captured: {region_filepath}")

            return str(full_filepath), str(region_filepath)

        except Exception as e:
            logging.error(f"Error capturing region: {str(e)}")
            return "", ""

    def capture_point_with_context(self, x: int, y: int, context_size: int = 100,
                                   delay: float = 0.0) -> Tuple[str, str, Dict[str, int]]:
        """
        Capture a point with surrounding context

        Args:
            x: X coordinate
            y: Y coordinate
            context_size: Size of context area around point (pixels)
            delay: Delay before capture in seconds

        Returns:
            Tuple of (full_screenshot_path, region_screenshot_path, region_dict)
        """
        # Calculate region bounds
        half_size = context_size // 2
        region_x = max(0, x - half_size)
        region_y = max(0, y - half_size)
        region_width = context_size
        region_height = context_size

        full_path, region_path = self.capture_region(
            region_x, region_y, region_width, region_height, delay
        )

        region_dict = {
            'x': region_x,
            'y': region_y,
            'width': region_width,
            'height': region_height
        }

        return full_path, region_path, region_dict

    def create_thumbnail(self, image_path: str, max_size: Tuple[int, int] = (150, 150)) -> str:
        """
        Create thumbnail from image

        Args:
            image_path: Path to source image
            max_size: Maximum thumbnail size (width, height)

        Returns:
            Path to thumbnail
        """
        try:
            img = Image.open(image_path)

            # Calculate thumbnail size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Generate thumbnail filename
            source_name = Path(image_path).stem
            thumb_filename = f"{source_name}_thumb.png"
            thumb_filepath = self.thumbnails_dir / thumb_filename

            # Save thumbnail
            img.save(str(thumb_filepath), 'PNG')
            logging.info(f"Thumbnail created: {thumb_filepath}")

            return str(thumb_filepath)

        except Exception as e:
            logging.error(f"Error creating thumbnail: {str(e)}")
            return ""

    def annotate_screenshot(self, screenshot_path: str, annotations: list) -> str:
        """
        Add annotations to screenshot (boxes, markers, labels)

        Args:
            screenshot_path: Path to screenshot
            annotations: List of annotation dicts with:
                - type: 'box' | 'point' | 'label'
                - x, y: coordinates
                - width, height: for boxes
                - color: annotation color
                - text: for labels

        Returns:
            Path to annotated image
        """
        try:
            img = Image.open(screenshot_path)
            draw = ImageDraw.Draw(img)

            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()

            for ann in annotations:
                ann_type = ann.get('type', 'box')
                color = ann.get('color', '#FF0000')
                x, y = ann.get('x', 0), ann.get('y', 0)

                if ann_type == 'box':
                    width, height = ann.get('width', 50), ann.get('height', 50)
                    # Draw rectangle
                    draw.rectangle(
                        [(x, y), (x + width, y + height)],
                        outline=color,
                        width=3
                    )

                elif ann_type == 'point':
                    # Draw crosshair
                    size = 10
                    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
                    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
                    # Draw circle
                    draw.ellipse([(x - 5, y - 5), (x + 5, y + 5)], outline=color, width=2)

                elif ann_type == 'label':
                    text = ann.get('text', '')
                    # Draw text with background
                    bbox = draw.textbbox((x, y), text, font=font)
                    draw.rectangle(bbox, fill='#000000AA')
                    draw.text((x, y), text, fill='white', font=font)

            # Save annotated image
            annotated_filename = Path(screenshot_path).stem + "_annotated.png"
            annotated_filepath = self.screenshots_dir / annotated_filename
            img.save(str(annotated_filepath), 'PNG')

            return str(annotated_filepath)

        except Exception as e:
            logging.error(f"Error annotating screenshot: {str(e)}")
            return screenshot_path

    def get_screen_resolution(self) -> Dict[str, int]:
        """Get current screen resolution"""
        size = pyautogui.size()
        return {
            'width': size.width,
            'height': size.height
        }

    def cleanup_old_screenshots(self, days: int = 30):
        """
        Remove screenshots older than specified days

        Args:
            days: Number of days to keep
        """
        cutoff_time = time.time() - (days * 86400)

        for directory in [self.screenshots_dir, self.thumbnails_dir, self.regions_dir]:
            for filepath in directory.glob("*.png"):
                if filepath.stat().st_mtime < cutoff_time:
                    try:
                        filepath.unlink()
                        logging.info(f"Deleted old screenshot: {filepath}")
                    except Exception as e:
                        logging.error(f"Error deleting {filepath}: {str(e)}")

    def create_action_preview(self, action_type: str, region_path: str,
                             output_size: Tuple[int, int] = (250, 70)) -> str:
        """
        Create a preview card image for an action

        Args:
            action_type: Type of action
            region_path: Path to region screenshot
            output_size: Size of output preview

        Returns:
            Path to preview image
        """
        try:
            # Create base image
            preview = Image.new('RGB', output_size, color='#FFFFFF')
            draw = ImageDraw.Draw(preview)

            # Load region image
            region_img = Image.open(region_path)

            # Resize region to fit in preview (left side)
            region_img.thumbnail((output_size[0] - 20, output_size[1] - 20),
                                Image.Resampling.LANCZOS)

            # Paste region image
            preview.paste(region_img, (10, 10))

            # Generate preview filename
            preview_filename = Path(region_path).stem + "_preview.png"
            preview_filepath = self.thumbnails_dir / preview_filename

            preview.save(str(preview_filepath), 'PNG')

            return str(preview_filepath)

        except Exception as e:
            logging.error(f"Error creating action preview: {str(e)}")
            return ""


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    manager = ScreenshotManager()

    # Test full screen capture
    print("Capturing full screen in 2 seconds...")
    full_path = manager.capture_full_screen(delay=2.0)
    print(f"Saved to: {full_path}")

    # Test thumbnail creation
    if full_path:
        thumb_path = manager.create_thumbnail(full_path)
        print(f"Thumbnail: {thumb_path}")

    # Test screen resolution
    resolution = manager.get_screen_resolution()
    print(f"Screen resolution: {resolution}")
