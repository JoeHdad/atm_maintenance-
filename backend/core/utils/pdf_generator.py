"""
PDF Generator for ATM Maintenance Reports
Generates a 5-page PDF report based on submission data
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image
import logging
import signal
from contextlib import contextmanager
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Timeout handler for PDF generation
class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    """Context manager to limit execution time"""
    def signal_handler(signum, frame):
        raise TimeoutException("PDF generation timed out")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)  # Disable the alarm


class PDFGenerator:
    """Generate PDF reports for ATM maintenance submissions"""
    
    def __init__(self, submission):
        self.submission = submission
        # Use landscape orientation: 297mm x 210mm
        self.width, self.height = landscape(A4)
        self.pdf_path = None
        # Cache for image dimensions to avoid repeated PIL operations
        self._image_cache = {}
        # Detect if this is an electrical device
        gfm_problem_type = (submission.device.gfm_problem_type or '').lower()
        self.is_electrical = (
            'electro' in gfm_problem_type and 'mechanical' in gfm_problem_type
        ) or 'electrical' in gfm_problem_type or submission.device.type == 'Electrical'
        
    def _preprocess_image(self, photo_path):
        """Preprocess a single image for faster rendering"""
        try:
            if not os.path.exists(photo_path):
                return None
            
            with Image.open(photo_path) as img:
                img_width, img_height = img.size
                
                # Resize large images for faster PDF rendering
                max_dimension = 2000
                if img_width > max_dimension or img_height > max_dimension:
                    ratio = min(max_dimension / img_width, max_dimension / img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    temp_path = photo_path + '.temp.jpg'
                    resized_img.save(temp_path, 'JPEG', quality=85, optimize=True)
                    
                    return (new_width, new_height, temp_path)
                else:
                    return (img_width, img_height, photo_path)
        except Exception as e:
            logger.error(f"Error preprocessing image {photo_path}: {str(e)}")
            return None
    
    def _preload_all_images(self):
        """Preload and resize all images in parallel for faster rendering"""
        photos = self.submission.photos.all()
        photo_paths = [os.path.join('media', photo.file_url) for photo in photos]
        
        # Process images in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_path = {executor.submit(self._preprocess_image, path): path for path in photo_paths}
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    if result:
                        self._image_cache[path] = result
                except Exception as e:
                    logger.error(f"Failed to preprocess {path}: {str(e)}")
    
    def generate(self):
        """
        Generate the complete 5-page PDF report
        Returns: Path to generated PDF file
        """
        import time
        start_time = time.time()
        
        try:
            # Preload all images in parallel before generating PDF
            preload_start = time.time()
            self._preload_all_images()
            logger.info(f"Images preloaded in {time.time() - preload_start:.2f}s")
            
            # Create PDF directory if it doesn't exist
            pdf_dir = os.path.join(settings.PDF_BASE_DIR, str(self.submission.id))
            os.makedirs(pdf_dir, exist_ok=True)

            # Track equivalent media-relative directory for storage
            media_relative_dir = os.path.join('media', 'pdfs', str(self.submission.id))
            
            # Generate PDF filename based on device type
            device_prefix = 'Electro' if self.is_electrical else 'Cleaning'
            filename = f"VisitReport_{device_prefix}_{self.submission.device.interaction_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            self.pdf_path = os.path.join(pdf_dir, filename)
            self.relative_pdf_path = os.path.join(media_relative_dir, filename)
            
            # Create PDF canvas with landscape orientation
            c = canvas.Canvas(self.pdf_path, pagesize=landscape(A4))
            
            # Generate pages based on device type
            page_start = time.time()
            self._generate_page1(c)  # Cover page
            logger.info(f"Page 1 generated in {time.time() - page_start:.2f}s")
            
            if self.is_electrical:
                # Electrical: 5 photo sections + checklist = 6 pages
                page_start = time.time()
                self._generate_electrical_page2(c)  # Section 1: 4 photos (2x2)
                logger.info(f"Page 2 (Electrical Section 1) generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_electrical_page3(c)  # Section 2: 4 photos (2x2)
                logger.info(f"Page 3 (Electrical Section 2) generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_electrical_page4(c)  # Section 3: 4 photos (2x2)
                logger.info(f"Page 4 (Electrical Section 3) generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_electrical_page5(c)  # Section 4: 4 photos (2x2)
                logger.info(f"Page 5 (Electrical Section 4) generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_electrical_page6(c)  # Section 5: 3 photos
                logger.info(f"Page 6 (Electrical Section 5) generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_page5(c)  # Checklist table (page 7 for electrical)
                logger.info(f"Page 7 (Checklist) generated in {time.time() - page_start:.2f}s")
            else:
                # Default Cleaning: 3 photo sections + checklist = 5 pages
                page_start = time.time()
                self._generate_page2(c)  # Section 1 photos
                logger.info(f"Page 2 generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_page3(c)  # Section 2 photos
                logger.info(f"Page 3 generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_page4(c)  # Section 3 photos
                logger.info(f"Page 4 generated in {time.time() - page_start:.2f}s")
                
                page_start = time.time()
                self._generate_page5(c)  # Checklist table
                logger.info(f"Page 5 generated in {time.time() - page_start:.2f}s")
            
            # Save PDF
            c.save()
            
            # Cleanup temporary resized images
            for cached_data in self._image_cache.values():
                if len(cached_data) == 3:  # (width, height, path)
                    temp_path = cached_data[2]
                    if temp_path.endswith('.temp.jpg') and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception as cleanup_error:
                            logger.warning(f"Failed to cleanup temp file {temp_path}: {str(cleanup_error)}")
            
            total_time = time.time() - start_time
            logger.info(f"PDF generated successfully in {total_time:.2f}s: {self.pdf_path}")
            return self.relative_pdf_path.replace('\\', '/')
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            # Cleanup temp files even on error
            for cached_data in self._image_cache.values():
                if len(cached_data) == 3:
                    temp_path = cached_data[2]
                    if temp_path.endswith('.temp.jpg') and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _generate_page1(self, c):
        """
        Page 1: Cover page with title, date, and ATM number
        Matches page1.png reference with dark teal gradient and number pattern
        """
        # Draw gradient background (dark black to dark teal)
        # Left side: darker (black), Right side: teal
        # Reduced strips for faster rendering (20 instead of 50)
        num_strips = 20
        for i in range(num_strips):
            # Gradient from black (0,0,0) on left to dark teal (0.1, 0.35, 0.35) on right
            ratio = i / num_strips
            r = 0.0 + (0.1 * ratio)
            g = 0.0 + (0.35 * ratio)
            b = 0.0 + (0.35 * ratio)
            c.setFillColorRGB(r, g, b)
            strip_width = self.width / num_strips
            c.rect(i * strip_width, 0, strip_width, self.height, fill=1, stroke=0)
        
        # Title - conditional based on device type
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 48)
        if self.is_electrical:
            c.drawString(40, self.height - 100, "PPM ELECTRO REPORT")
        else:
            c.drawString(40, self.height - 100, "PPM CLEANING REPORT")
        
        # Subtitle
        c.setFont("Helvetica", 24)
        c.drawString(40, self.height - 140, "( Drive Throw )")
        
        # Visit date (dynamic)
        visit_date = self.submission.created_at.strftime('%d/%B/ %Y')
        c.setFont("Helvetica", 16)
        c.drawString(40, self.height - 250, f"Visit date :{visit_date}")
        
        # ATM number (dynamic - from cost center)
        cost_center = self.submission.device.gfm_cost_center
        c.setFont("Helvetica-Bold", 36)
        c.drawString(40, self.height - 320, f"ATM # {cost_center}")
        
        # Picture1.jpg logo at bottom-left corner
        try:
            logo_path = os.path.join('media', 'Picture1.jpg')
            if os.path.exists(logo_path):
                # Place logo at bottom-left with proper sizing
                c.drawImage(logo_path, 40, 30, width=120, height=80, preserveAspectRatio=True, mask='auto')
            else:
                # Fallback text if logo not available
                c.setFont("Helvetica-Bold", 24)
                c.drawString(40, 60, "Logo")
        except Exception as e:
            logger.warning(f"Could not load Picture1.jpg on page 1: {str(e)}")
            c.setFont("Helvetica-Bold", 24)
            c.drawString(40, 60, "Logo")
        
        c.showPage()
    
    def _generate_page2(self, c):
        """
        Page 2: Section 1 photos (Site Machine - 3-5m away)
        Landscape layout: vertical sidebar on right, photos filling full height
        """
        # Get Section 1 photos
        photos = self.submission.photos.filter(section=1).order_by('order_index')[:3]
        
        # Draw vertical sidebar on right
        self._draw_vertical_sidebar(c, 
            title="Cleaning. Site Machine",
            instructions="Photos must be clear, also showing machine and pylon from four sides from 3 to 5 meters away",
            note="Site Machine not Less than 4 Photos"
        )
        
        # Draw photos filling full height from top to bottom
        self._draw_full_height_photos(c, photos)
        
        c.showPage()
    
    def _generate_page3(self, c):
        """
        Page 3: Section 2 photos (Site Machine - Zoom)
        Landscape layout: vertical sidebar on right, photos filling full height
        """
        # Get Section 2 photos
        photos = self.submission.photos.filter(section=2).order_by('order_index')[:3]
        
        # Draw vertical sidebar on right
        self._draw_vertical_sidebar(c,
            title="Cleaning. Site Machine",
            instructions="Zoom in and out for front and back from 3 to 5 meters away",
            note="Site Machine not Less than 4 Photos"
        )
        
        # Draw photos filling full height from top to bottom
        self._draw_full_height_photos(c, photos)
        
        c.showPage()
    
    def _generate_page4(self, c):
        """
        Page 4: Section 3 photos (Civil and Site)
        Landscape layout: vertical sidebar on right, photos filling full height
        """
        # Get Section 3 photos
        photos = self.submission.photos.filter(section=3).order_by('order_index')[:2]
        
        # Draw vertical sidebar on right
        self._draw_vertical_sidebar(c,
            title="Cleaning. Civil and Site",
            instructions="Photo for Asphalt and pavement from more than onsite with security column",
            note="Photos Not Showing Maintenance Team"
        )
        
        # Draw photos filling full height from top to bottom (2 photos)
        self._draw_full_height_photos(c, photos)
        
        c.showPage()
    
    def _generate_electrical_page2(self, c):
        """
        Electrical Page 2: Section 1 photos (4 photos in 2x2 grid)
        """
        photos = self.submission.photos.filter(section=1).order_by('order_index')[:4]
        
        self._draw_vertical_sidebar(c, 
            title="Electro. Site Machine",
            instructions="Photos must be Nightly and clear, also showing machine and pylon from four sides from 3 to 5 meters away.",
            note="Site Machine not Less than 4 Photos"
        )
        
        self._draw_2x2_grid_photos(c, photos)
        c.showPage()
    
    def _generate_electrical_page3(self, c):
        """
        Electrical Page 3: Section 2 photos (4 photos in 2x2 grid)
        """
        photos = self.submission.photos.filter(section=2).order_by('order_index')[:4]
        
        self._draw_vertical_sidebar(c,
            title="Electro. Site Machine",
            instructions="Photos must be Nightly and clear. Zoom in and out for front and back from 3 to 5 meters away.",
            note="Site Machine not Less than 4 Photos"
        )
        
        self._draw_2x2_grid_photos(c, photos)
        c.showPage()
    
    def _generate_electrical_page4(self, c):
        """
        Electrical Page 4: Section 3 photos (4 photos in 2x2 grid)
        """
        photos = self.submission.photos.filter(section=3).order_by('order_index')[:4]
        
        self._draw_vertical_sidebar(c,
            title="Electro. Equipment",
            instructions="Photos must be clear, also showing HVAC Temperature, Power voltmeter, Internally Light & Externally Light.",
            note="Equipment Photos Required"
        )
        
        self._draw_2x2_grid_photos(c, photos)
        c.showPage()
    
    def _generate_electrical_page5(self, c):
        """
        Electrical Page 5: Section 4 photos (4 photos in 2x2 grid)
        """
        photos = self.submission.photos.filter(section=4).order_by('order_index')[:4]
        
        self._draw_vertical_sidebar(c,
            title="Electro. Components",
            instructions="Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.",
            note="Component Photos Required"
        )
        
        self._draw_2x2_grid_photos(c, photos)
        c.showPage()
    
    def _generate_electrical_page6(self, c):
        """
        Electrical Page 6: Section 5 photos (3 photos)
        """
        photos = self.submission.photos.filter(section=5).order_by('order_index')[:3]
        
        self._draw_vertical_sidebar(c,
            title="Electro. Final Check",
            instructions="Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.",
            note="Final Check Photos Required"
        )
        
        self._draw_full_height_photos(c, photos)
        c.showPage()
    
    def _draw_2x2_grid_photos(self, c, photos):
        """Draw 4 photos in a 2x2 grid layout (for electrical sections) with no gaps"""
        # Calculate available space (excluding sidebar)
        sidebar_width = 150
        available_width = self.width - sidebar_width
        available_height = self.height
        
        # Calculate photo dimensions for 2x2 grid (no spacing between photos)
        photo_width = available_width / 2
        photo_height = available_height / 2
        
        # Grid positions: [top-left, top-right, bottom-left, bottom-right]
        # No spacing - photos are tightly aligned
        positions = [
            (0, photo_height),  # Top-left
            (photo_width, photo_height),  # Top-right
            (0, 0),  # Bottom-left
            (photo_width, 0)  # Bottom-right
        ]
        
        for i, photo in enumerate(photos):
            if i >= 4:  # Only draw 4 photos max
                break
                
            x, y = positions[i]
            
            try:
                photo_path = os.path.join('media', photo.file_url)
                
                if os.path.exists(photo_path):
                    try:
                        # Draw image to fill entire grid cell - no gaps, no cropping
                        # Image will be stretched to fit if aspect ratio doesn't match
                        c.drawImage(photo_path, x, y, 
                                  width=photo_width, height=photo_height, 
                                  preserveAspectRatio=False, mask='auto')
                        
                        # Note: preserveAspectRatio=False allows image to stretch to fill
                        # entire cell, eliminating gaps while keeping full image visible
                    except Exception as img_error:
                        logger.error(f"Error processing image {photo.id}: {str(img_error)}")
                        # Draw error placeholder
                        c.setFillColorRGB(0.9, 0.9, 0.9)
                        c.rect(x, y, photo_width, photo_height, fill=1)
                        c.setFillColorRGB(0.5, 0.5, 0.5)
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(x + photo_width/2, y + photo_height/2, "Error loading image")
                else:
                    # Draw placeholder if photo not found
                    logger.warning(f"Photo file not found: {photo_path}")
                    c.setFillColorRGB(0.9, 0.9, 0.9)
                    c.rect(x, y, photo_width, photo_height, fill=1)
                    c.setFillColorRGB(0.5, 0.5, 0.5)
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x + photo_width/2, y + photo_height/2, "Photo not found")
                    
            except Exception as e:
                logger.error(f"Error drawing photo {photo.id}: {str(e)}")
                # Draw error placeholder
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, y, photo_width, photo_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.setFont("Helvetica", 12)
                c.drawCentredString(x + photo_width/2, y + photo_height/2, "Error loading photo")
    
    def _generate_page5(self, c):
        """
        Page 5: Preventive Cleaning Checklist - matches reference image exactly
        """
        # Draw sidebar first (right side, dark green with pattern)
        sidebar_width = 150  # Match pages 2, 3, 4 sidebar width
        sidebar_x = self.width - sidebar_width
        
        # Dark green sidebar background
        c.setFillColorRGB(0, 0.31, 0.24)
        c.rect(sidebar_x, 0, sidebar_width, self.height, fill=1, stroke=0)
        
        # Sidebar text - "Remarks Maintenance Team"
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 18)  # Slightly smaller to fit better
        c.drawString(sidebar_x + 10, self.height / 2 + 80, "Remarks")
        c.drawString(sidebar_x + 10, self.height / 2 + 55, "Maintenance")
        c.drawString(sidebar_x + 10, self.height / 2 + 30, "Team")
        
        # Sidebar note at bottom
        c.setFont("Helvetica", 8)  # Slightly smaller to fit
        note_y = 100
        c.drawString(sidebar_x + 10, note_y, "Check List must be")
        c.drawString(sidebar_x + 10, note_y - 12, "completed also")
        c.drawString(sidebar_x + 10, note_y - 24, "match with site")
        c.drawString(sidebar_x + 10, note_y - 36, "status")
        
        # Main content area (left side)
        content_width = sidebar_x - 20
        
        # Picture1.jpg logo at top-left corner (flush with top)
        try:
            logo1_path = os.path.join('media', 'Picture1.jpg')
            if os.path.exists(logo1_path):
                logo1_width = 100
                logo1_height = 40
                logo1_x = 10
                logo1_y = self.height - logo1_height - 5  # 5px from top edge
                c.drawImage(logo1_path, logo1_x, logo1_y, width=logo1_width, height=logo1_height,
                           preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logger.warning(f"Could not load Picture1.jpg on page 5: {str(e)}")
        
        # SNB Logo at top right (flush with top)
        try:
            logo2_path = os.path.join('media', 'Picture2.jpg')
            if os.path.exists(logo2_path):
                logo_width = 100
                logo_height = 40
                logo_x = content_width - logo_width - 10
                logo_y = self.height - logo_height - 5  # 5px from top edge
                c.drawImage(logo2_path, logo_x, logo_y, width=logo_width, height=logo_height,
                           preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logger.warning(f"Could not load Picture2.jpg on page 5: {str(e)}")
        
        # Title (aligned with logos) - conditional based on device type
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 12)
        if self.is_electrical:
            c.drawCentredString(content_width / 2, self.height - 25, "Preventive Maintenance Checklist - Drive Up")  # Electrical title
        else:
            c.drawCentredString(content_width / 2, self.height - 25, "Preventive Cleaning Checklist")  # Cleaning title
        
        # Header table with ATM info
        y = self.height - 55
        self._draw_page5_header_table(c, y, content_width)
        
        # Checklist table
        y -= 50
        checklist_end_y = self._draw_page5_checklist_table(c, y, content_width)
        
        # Remarks row
        remarks_y = checklist_end_y - 20
        self._draw_page5_remarks_row(c, remarks_y, content_width)
        
        # Signature table at bottom
        signature_y = remarks_y - 40
        self._draw_page5_signature_table(c, signature_y, content_width)
        
        c.showPage()
    
    def _draw_header(self, c, title, instructions, note):
        """Draw horizontal header at top with gradient background matching page 1"""
        # Header height
        header_height = 100
        
        # Draw gradient background (same as page 1: black to dark teal)
        num_strips = 50
        for i in range(num_strips):
            # Gradient from black (0,0,0) on left to dark teal (0.1, 0.35, 0.35) on right
            ratio = i / num_strips
            r = 0.0 + (0.1 * ratio)
            g = 0.0 + (0.35 * ratio)
            b = 0.0 + (0.35 * ratio)
            c.setFillColorRGB(r, g, b)
            strip_width = self.width / num_strips
            c.rect(i * strip_width, self.height - header_height, strip_width, header_height, fill=1, stroke=0)
        
        # Title - centered horizontally
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 16)
        y = self.height - 25
        title_text = title.replace('\n', ' ')
        c.drawCentredString(self.width / 2, y, title_text)
        
        # Instructions - centered horizontally
        y -= 25
        c.setFont("Helvetica", 10)
        instructions_text = instructions.replace('\n', ' ')
        c.drawCentredString(self.width / 2, y, instructions_text)
        
        # Note - centered horizontally with darker background
        y -= 30
        note_width = 400
        note_x = (self.width - note_width) / 2
        c.setFillColorRGB(0.15, 0.4, 0.4)
        c.rect(note_x, y - 20, note_width, 25, fill=1, stroke=0)
        
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 9)
        note_text = note.replace('\n', ' ')
        c.drawCentredString(self.width / 2, y - 7, note_text)
    
    def _draw_vertical_sidebar(self, c, title, instructions, note):
        """Draw vertical sidebar with vertically centered text block"""
        # Sidebar dimensions
        sidebar_width = 150  # Width of sidebar
        sidebar_x = self.width - sidebar_width  # Position at right edge
        
        # Draw solid dark green background (matching reference image)
        c.setFillColorRGB(0, 0.31, 0.24)  # Dark green
        c.rect(sidebar_x, 0, sidebar_width, self.height, fill=1, stroke=0)
        
        # Prepare all text elements first to calculate total height
        max_width = sidebar_width - 20  # 10px padding each side
        
        # Title - wrap if needed
        c.setFont("Helvetica-Bold", 14)
        title_lines = []
        words = title.split()
        current_line = ""
        
        for word in words:
            test_line = (current_line + " " + word).strip()
            text_width = c.stringWidth(test_line, "Helvetica-Bold", 14)
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    title_lines.append(current_line)
                current_line = word
        if current_line:
            title_lines.append(current_line)
        
        # Instructions - wrap text
        c.setFont("Helvetica", 9)
        instruction_lines = []
        words = instructions.split()
        current_line = ""
        
        for word in words:
            test_line = (current_line + " " + word).strip()
            text_width = c.stringWidth(test_line, "Helvetica", 9)
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    instruction_lines.append(current_line)
                current_line = word
        if current_line:
            instruction_lines.append(current_line)
        
        # Note - wrap text
        c.setFont("Helvetica", 8)
        note_lines = []
        words = note.split()
        current_line = ""
        note_max_width = sidebar_width - 30
        
        for word in words:
            test_line = (current_line + " " + word).strip()
            text_width = c.stringWidth(test_line, "Helvetica", 8)
            if text_width <= note_max_width:
                current_line = test_line
            else:
                if current_line:
                    note_lines.append(current_line)
                current_line = word
        if current_line:
            note_lines.append(current_line)
        
        # Calculate total height of all content
        title_height = len(title_lines) * 18  # 18px per title line
        space_after_title = 20  # Space between title and instructions
        instructions_height = len(instruction_lines) * 12  # 12px per instruction line
        space_before_note = 20  # Space between instructions and note
        note_height = 40  # Note box height
        
        total_content_height = title_height + space_after_title + instructions_height + space_before_note + note_height
        
        # Calculate starting Y position to center the entire block
        start_y = (self.height + total_content_height) / 2
        
        # Draw title lines (centered vertically)
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 14)
        y = start_y
        for line in title_lines:
            c.drawString(sidebar_x + 10, y, line)
            y -= 18
        
        # Space after title
        y -= space_after_title
        
        # Draw instruction lines
        c.setFont("Helvetica", 9)
        for line in instruction_lines:
            c.drawString(sidebar_x + 10, y, line)
            y -= 12
        
        # Space before note
        y -= space_before_note
        
        # Draw note box (positioned relative to text flow)
        note_y = y - note_height
        c.setFillColorRGB(0.1, 0.4, 0.35)  # Lighter green box
        c.rect(sidebar_x + 5, note_y, sidebar_width - 10, note_height, fill=1, stroke=0)
        
        # Draw note text inside box
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica", 8)
        note_text_y = note_y + note_height - 12
        for line in note_lines:
            c.drawString(sidebar_x + 10, note_text_y, line)
            note_text_y -= 10
    
    def _draw_full_height_photos(self, c, photos):
        """Draw photos filling full page height from top to bottom, divided equally"""
        num_photos = len(photos)
        if num_photos == 0:
            return
        
        # Calculate available width (excluding sidebar)
        sidebar_width = 150
        available_width = self.width - sidebar_width
        available_height = self.height  # Full page height
        
        # Calculate photo width based on number of photos
        photo_width = available_width / num_photos
        
        # Draw each photo
        x = 0
        for i, photo in enumerate(photos):
            try:
                # Get photo path
                photo_path = os.path.join('media', photo.file_url)
                
                if os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path)
                        
                        # Calculate aspect ratio
                        img_width, img_height = img.size
                        aspect_ratio = img_width / img_height
                        
                        # Strategy: Compress horizontally to fit full width within frame
                        # Keep full height (595px) - no vertical changes
                        draw_height = available_height  # Full page height (595px)
                        
                        # Calculate natural width at full height
                        natural_width = available_height * aspect_ratio
                        
                        # If image would be wider than allocated space, compress it horizontally
                        # to fit the full original image width within the frame
                        if natural_width > photo_width:
                            # Compress horizontally to fit within photo_width
                            draw_width = photo_width
                            x_offset = 0  # No offset needed, fits exactly
                        else:
                            # Image narrower than space - use natural width and center
                            draw_width = natural_width
                            x_offset = (photo_width - draw_width) / 2
                        
                        # Always start from bottom edge (y=0) to fill complete height
                        y_offset = 0
                        
                        # Create clipping path to ensure image stays within boundaries
                        c.saveState()
                        path = c.beginPath()
                        path.rect(x, 0, photo_width, available_height)
                        c.clipPath(path, stroke=0)
                        
                        # Draw image with horizontal compression if needed
                        # Height always full (595px), width compressed to fit
                        c.drawImage(photo_path, x + x_offset, y_offset, 
                                  width=draw_width, height=draw_height, 
                                  preserveAspectRatio=False, mask='auto')  # Allow horizontal compression
                        
                        c.restoreState()
                        
                        # Close image to free memory
                        img.close()
                    except Exception as img_error:
                        logger.error(f"Error processing image {photo.id}: {str(img_error)}")
                        # Draw error placeholder
                        c.setFillColorRGB(0.9, 0.9, 0.9)
                        c.rect(x, 0, photo_width, available_height, fill=1)
                        c.setFillColorRGB(0.5, 0.5, 0.5)
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(x + photo_width/2, available_height/2, "Error loading image")
                else:
                    # Draw placeholder if photo not found
                    logger.warning(f"Photo file not found: {photo_path}")
                    c.setFillColorRGB(0.9, 0.9, 0.9)
                    c.rect(x, 0, photo_width, available_height, fill=1)
                    c.setFillColorRGB(0.5, 0.5, 0.5)
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x + photo_width/2, available_height/2, "Photo not found")
                
                x += photo_width
                
            except Exception as e:
                logger.error(f"Error drawing photo {photo.id}: {str(e)}")
                # Draw error placeholder and continue
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, 0, photo_width, available_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.setFont("Helvetica", 12)
                c.drawCentredString(x + photo_width/2, available_height/2, "Error loading photo")
                x += photo_width
    
    def _draw_photo_row(self, c, photos, header_height=100):
        """Draw photos filling entire page height from header to bottom edge"""
        # Calculate available space - full height from header to bottom
        side_margin = 30  # Keep side margins for horizontal spacing
        available_width = self.width - (2 * side_margin)
        available_height = self.height - header_height  # Full height from header to bottom (no top/bottom margins)
        
        num_photos = len(photos)
        if num_photos == 0:
            return
        
        # Calculate photo dimensions based on number of photos
        spacing = 20
        if num_photos == 1:
            # Single photo: centered, full width
            photo_width = available_width
            photo_height = available_height
            x_start = side_margin
        elif num_photos == 2:
            # Two photos: half width each
            photo_width = (available_width - spacing) / 2
            photo_height = available_height
            x_start = side_margin
        else:  # 3 or more photos
            # Three photos: equal width
            photo_width = (available_width - (2 * spacing)) / 3
            photo_height = available_height
            x_start = side_margin
        
        # Starting Y position (from bottom of header to bottom of page)
        y_position = self.height - header_height  # Start right below header
        
        x = x_start
        for i, photo in enumerate(photos):
            try:
                # Get photo path
                photo_path = os.path.join('media', photo.file_url)
                
                if os.path.exists(photo_path):
                    # Use preloaded image from cache
                    try:
                        if photo_path in self._image_cache:
                            img_width, img_height, render_path = self._image_cache[photo_path]
                        else:
                            # Fallback: load image if not in cache (shouldn't happen with preloading)
                            with Image.open(photo_path) as img:
                                img_width, img_height = img.size
                                render_path = photo_path
                        
                        # Calculate aspect ratio to maintain quality
                        aspect_ratio = img_width / img_height
                        
                        # Fit image within allocated space while maintaining aspect ratio
                        if aspect_ratio > (photo_width / photo_height):
                            # Width is limiting factor
                            draw_width = photo_width
                            draw_height = photo_width / aspect_ratio
                        else:
                            # Height is limiting factor
                            draw_height = photo_height
                            draw_width = photo_height * aspect_ratio
                        
                        # Center image within allocated space
                        x_offset = (photo_width - draw_width) / 2
                        y_offset = (photo_height - draw_height) / 2
                        
                        # Draw photo with optimized image (centered in allocated space)
                        c.drawImage(ImageReader(render_path), x + x_offset, y_position - draw_height - y_offset, 
                                  width=draw_width, height=draw_height, 
                                  preserveAspectRatio=True, mask='auto')
                    except Exception as img_error:
                        logger.error(f"Error processing image {photo.id}: {str(img_error)}")
                        # Draw error placeholder
                        c.setFillColorRGB(0.9, 0.9, 0.9)
                        c.rect(x, y_position - photo_height, photo_width, photo_height, fill=1)
                        c.setFillColorRGB(0.5, 0.5, 0.5)
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(x + photo_width/2, y_position - photo_height/2, "Error loading image")
                else:
                    # Draw placeholder if photo not found
                    logger.warning(f"Photo file not found: {photo_path}")
                    c.setFillColorRGB(0.9, 0.9, 0.9)
                    c.rect(x, y_position - photo_height, photo_width, photo_height, fill=1)
                    c.setFillColorRGB(0.5, 0.5, 0.5)
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x + photo_width/2, y_position - photo_height/2, "Photo not found")
                
                x += photo_width + spacing
                
            except Exception as e:
                logger.error(f"Error drawing photo {photo.id}: {str(e)}")
                # Draw error placeholder and continue
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, y_position - photo_height, photo_width, photo_height, fill=1)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.setFont("Helvetica", 12)
                c.drawCentredString(x + photo_width/2, y_position - photo_height/2, "Error loading photo")
                x += photo_width + spacing
    
    def _draw_table_header_row(self, c, y, fields):
        """Draw the header row with dynamic fields - adjusted for landscape"""
        x = 40
        # More width available in landscape
        cell_width = (self.width - 100) / len(fields)
        
        c.setFont("Helvetica-Bold", 9)
        for label, value in fields:
            # Draw cell border
            c.rect(x, y, cell_width, 30)
            
            # Draw label
            if label:
                c.drawString(x + 5, y + 18, label)
            
            # Draw value
            c.setFont("Helvetica", 9)
            c.drawString(x + 5, y + 5, str(value))
            c.setFont("Helvetica-Bold", 9)
            
            x += cell_width
    
    def _draw_page5_header_table(self, c, y, content_width):
        """Draw header table with ATM information (single row only)"""
        row_height = 20
        
        # Calculate column widths to span full content width (touching sidebar)
        sidebar_width = 150
        table_width = self.width - sidebar_width - 10
        
        x_start = 10
        x = x_start
        
        # Single row with ATM info
        col_widths = [40, 60, 40, 60, 50, 60, 100, 50, 70]
        
        # ATM (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[0], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[0]/2, y + 6, "ATM")
        x += col_widths[0]
        
        # ATM value
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[1], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + col_widths[1]/2, y + 6, str(self.submission.device.gfm_cost_center))
        x += col_widths[1]
        
        # Type (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[2], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[2]/2, y + 6, "Type")
        x += col_widths[2]
        
        # Type value - conditional based on device type
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[3], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        if self.is_electrical:
            c.drawCentredString(x + col_widths[3]/2, y + 6, "Electro")
        else:
            c.drawCentredString(x + col_widths[3]/2, y + 6, "Cleaning")
        x += col_widths[3]
        
        # Region (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[4], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[4]/2, y + 6, "Region")
        x += col_widths[4]
        
        # South value
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[5], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + col_widths[5]/2, y + 6, "South")
        x += col_widths[5]
        
        # City row below
        y -= row_height
        x = x_start + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3]
        
        # City (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[4], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[4]/2, y + 6, "City")
        x += col_widths[4]
        
        # City value - conditional based on device type
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[5], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        if self.is_electrical:
            c.drawCentredString(x + col_widths[5]/2, y + 6, "Hail")
        else:
            c.drawCentredString(x + col_widths[5]/2, y + 6, self.submission.device.city)
        
        # Back to first row for remaining columns
        y += row_height
        x = x_start + sum(col_widths[0:6])
        
        # GFM Code (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[6], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + col_widths[6]/2, y + 6, self.submission.device.interaction_id)
        x += col_widths[6]
        
        # DATE (gray header)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[7], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[7]/2, y + 6, "DATE")
        x += col_widths[7]
        
        # Date value
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[8], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + col_widths[8]/2, y + 6, self.submission.created_at.strftime('%d.%m.%Y'))
    
    def _draw_page5_checklist_table(self, c, y, content_width):
        """Draw checklist items table with Job Description, Status, Remarks headers"""
        # Calculate widths to span full content width (touching sidebar)
        sidebar_width = 150
        table_width = self.width - sidebar_width - 10
        col_widths = [table_width - 300, 50, 50, 200]
        
        row_height = 15
        x_start = 10
        
        # Header row: Job Description | Status | (blank) | Remarks
        x = x_start
        
        # Job Description header
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[0], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[0]/2, y + 4, "Job Description")
        x += col_widths[0]
        
        # Status header (spans 2 columns: Ok and Not Ok)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y, col_widths[1] + col_widths[2], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + (col_widths[1] + col_widths[2])/2, y + 4, "Status")
        
        # Sub-headers: Ok and Not Ok
        y -= row_height
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[1], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + col_widths[1]/2, y + 4, "Ok")
        x += col_widths[1]
        
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y, col_widths[2], row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + col_widths[2]/2, y + 4, "Not Ok")
        x += col_widths[2]
        
        # Remarks header (spans 2 rows)
        y += row_height
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(x, y - row_height, col_widths[3], row_height * 2, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + col_widths[3]/2, y - row_height/2 + 4, "Remarks")
        
        # Data rows - conditional based on device type
        y -= row_height
        
        if self.is_electrical:
            # Electrical checklist - with category headers
            items = [
                ("[Air Conditioner (A/C)]", True),
                ("Clean A/C Filter", False),
                ("Check A/C Drainage", False),
                ("Check For A/C Sound Vibration, Bearing", False),
                ("Check A/C Temperature - With Picture", False),
                ("[Electronically]", True),
                ("Check And Clean Lamps / Switches", False),
                ("Check And Clean Convenience Outlets", False),
                ("Check And Clean Stabilizer / UPS", False),
                ("Check And Clean Insider", False),
                ("Check Timer and Retimed", False),
                ("Change Busted Light", False),
                ("Arrange Cable and Covered", False),
                ("[Panel Boards]", True),
                ("Check And Clean Panel Boards", False),
                ("Retightening Of Wires and Cable Arrangements", False),
                ("Neutral To Ground (Less Than 2v)", False),
                ("[Carpentry / Civil Works]", True),
                ("Check Door Hinges, Locks, Door Closer and Apply Grease", False),
                ("Check For Holes and Cracks in The Cabinet", False),
                ("Check Floor Tiles, Stairs, Paintings, Ceiling, And Glass, etc.", False),
                ("Pavement Painting", False),
                ("Check Asphalt, Boundary, Curb Stone, Security Poles", False),
            ]
        else:
            # Cleaning checklist - with header rows
            items = [
                ("Cleaning", True),
                ("Inside Room & Glass", False),
                ("Polishing Of Ground Tiles/Marble", False),
                ("Inside Kiosk/Top of Kiosk", False),
                ("A/C And Lighting Grills", False),
                ("Totem", False),
                ("Rust", False),
                ("Drain Pipe", False),
                ("Clean Ground Light", False),
                ("Clean Pavement", False),
                ("Branding", True),
                ("Drive Thru", True),
                ("Pylon (Logo, Letters, Sticker, Light, Acrylic and Posters)", False),
                ("Kiosk (Logo, Letters, Sticker, Light, Acrylic and Posters)", False),
                ("Unipolar & Canopy Sticker", False),
                ("TID Plate", False),
                ("QR Plate", False),
                ("Lobby / Window", True),
                ("Signage ( Logo – Letters )", False),
                ("SNB Sticker", False),
                ("Poster On Glass", False),
                ("Trash Bin Fire Resister", False),
                ("Kiosk (Logo – Letters – Posters – Acrylic )", False),
                ("QR Plate", False),
            ]
        
        for item, is_header in items:
            y -= row_height
            x = x_start
            
            # Job description
            if is_header:
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.rect(x, y, col_widths[0], row_height, fill=1, stroke=1)
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", 8)
                c.drawCentredString(x + col_widths[0]/2, y + 4, item)
            else:
                c.setFillColorRGB(1, 1, 1)
                c.rect(x, y, col_widths[0], row_height, fill=1, stroke=1)
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica", 7)
                c.drawString(x + 3, y + 4, item)
            x += col_widths[0]
            
            # Ok column - fill with "Ok" for all non-header rows
            c.setFillColorRGB(1, 1, 1)
            c.rect(x, y, col_widths[1], row_height, fill=1, stroke=1)
            if not is_header:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica", 7)
                c.drawCentredString(x + col_widths[1]/2, y + 4, "Ok")
            x += col_widths[1]
            
            # Not Ok column
            c.setFillColorRGB(1, 1, 1)
            c.rect(x, y, col_widths[2], row_height, fill=1, stroke=1)
            x += col_widths[2]
            
            # Remarks column
            c.setFillColorRGB(1, 1, 1)
            c.rect(x, y, col_widths[3], row_height, fill=1, stroke=1)
        
        return y
    
    def _draw_page5_remarks_row(self, c, y, content_width):
        """Draw remarks instruction row"""
        row_height = 15
        sidebar_width = 150
        table_width = self.width - sidebar_width - 10  # Touch sidebar
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(10, y, table_width, row_height, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 7)
        c.drawString(15, y + 4, "Remarks :                  Kindly Review the ATM Receipt Taken on The Same Day Before Signature")
    
    def _draw_page5_signature_table(self, c, y, content_width):
        """Draw signature table at bottom"""
        row_height = 25
        sidebar_width = 150
        table_width = self.width - sidebar_width - 10  # Touch sidebar
        col_width = table_width / 2
        
        # Header row
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(10, y, col_width, row_height, fill=1, stroke=1)
        c.rect(10 + col_width, y, col_width, row_height, fill=1, stroke=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(10 + col_width/2, y + 8, "Technician / Supervisor")
        c.drawCentredString(10 + col_width + col_width/2, y + 8, "Project Manager")
        
        # Name row - conditional based on device type
        y -= row_height
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.rect(10, y, col_width, row_height, fill=1, stroke=1)
        c.rect(10 + col_width, y, col_width, row_height, fill=1, stroke=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        if self.is_electrical:
            c.drawCentredString(10 + col_width/2, y + 8, "M.ISHTIAQ")
        else:
            c.drawCentredString(10 + col_width/2, y + 8, "Ahmad Javed")
        c.drawCentredString(10 + col_width + col_width/2, y + 8, "Fahad Abdul Ghaffar")
    
    def _draw_remarks_table(self, c, y):
        """Draw the remarks table at bottom with 2 columns and 2 rows"""
        # Table dimensions
        table_width = self.width - 80
        col_width = table_width / 2
        row_height = 30
        
        # Starting position for table
        table_y = y
        
        # Draw table borders
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        
        # Outer rectangle
        c.rect(40, table_y - (2 * row_height), table_width, 2 * row_height)
        
        # Vertical line (separating columns)
        c.line(40 + col_width, table_y - (2 * row_height), 40 + col_width, table_y)
        
        # Horizontal line (separating rows)
        c.line(40, table_y - row_height, 40 + table_width, table_y - row_height)
        
        # Row 1: Headers with gray background
        c.setFillColorRGB(0.85, 0.85, 0.85)  # Light gray background
        c.rect(40, table_y - row_height, col_width, row_height, fill=1, stroke=0)
        c.rect(40 + col_width, table_y - row_height, col_width, row_height, fill=1, stroke=0)
        
        # Row 1: Header text
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(40 + col_width/2, table_y - row_height + 10, "Technician / Supervisor")
        c.drawCentredString(40 + col_width + col_width/2, table_y - row_height + 10, "Project Manager")
        
        # Row 2: Names with gray background
        c.setFillColorRGB(0.85, 0.85, 0.85)  # Light gray background
        c.rect(40, table_y - (2 * row_height), col_width, row_height, fill=1, stroke=0)
        c.rect(40 + col_width, table_y - (2 * row_height), col_width, row_height, fill=1, stroke=0)
        
        # Row 2: Name text
        c.setFillColorRGB(0, 0, 0)  # Black text
        c.setFont("Helvetica", 10)
        c.drawCentredString(40 + col_width/2, table_y - (2 * row_height) + 10, "Ahmad Javed")
        
        # Fahad Abdul Ghaffar in blue (as shown in image)
        c.setFillColorRGB(0, 0, 1)  # Blue text
        c.drawCentredString(40 + col_width + col_width/2, table_y - (2 * row_height) + 10, "Fahad Abdul Ghaffar")
        
        # Redraw borders on top to ensure they're visible
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(40, table_y - (2 * row_height), table_width, 2 * row_height, fill=0, stroke=1)
        c.line(40 + col_width, table_y - (2 * row_height), 40 + col_width, table_y)
        c.line(40, table_y - row_height, 40 + table_width, table_y - row_height)
    
    def _draw_signature_section(self, c, y):
        """Draw the signature section at bottom (DEPRECATED - replaced by _draw_remarks_table)"""
        # Two columns
        col_width = (self.width - 80) / 2
        
        # Left column - Technician/Supervisor
        c.rect(40, y, col_width, 80)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(40 + col_width/2, y + 60, "Technician / Supervisor")
        c.setFont("Helvetica", 10)
        c.drawCentredString(40 + col_width/2, y + 20, "Ahmed Javed")
        
        # Right column - Project Manager
        c.rect(40 + col_width, y, col_width, 80)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(40 + col_width + col_width/2, y + 60, "Project Manager")
        c.setFont("Helvetica", 10)
        c.drawCentredString(40 + col_width + col_width/2, y + 20, "Fahed Abdul Ghaffar")


def generate_pdf(submission):
    """
    Main function to generate PDF for a submission
    
    Args:
        submission: Submission model instance
        
    Returns:
        str: Relative path to generated PDF file
        
    Raises:
        Exception: If PDF generation fails
    """
    try:
        # Check if PDF already exists and is recent (within last 5 minutes)
        if submission.pdf_url:
            pdf_path = os.path.join(submission.pdf_url)
            if os.path.exists(pdf_path):
                # Check file modification time
                file_mtime = os.path.getmtime(pdf_path)
                current_time = datetime.now().timestamp()
                # If PDF is less than 5 minutes old, reuse it
                if (current_time - file_mtime) < 300:  # 300 seconds = 5 minutes
                    logger.info(f"Reusing existing PDF for submission {submission.id}: {submission.pdf_url}")
                    return submission.pdf_url
        
        # Generate new PDF with timeout protection (30 seconds max)
        logger.info(f"Generating new PDF for submission {submission.id}")
        generator = PDFGenerator(submission)
        pdf_path = generator.generate()
        return pdf_path
    except TimeoutException as e:
        logger.error(f"PDF generation timed out for submission {submission.id}: {str(e)}")
        raise Exception("PDF generation timed out. Please try again.")
    except Exception as e:
        logger.error(f"PDF generation failed for submission {submission.id}: {str(e)}")
        raise
