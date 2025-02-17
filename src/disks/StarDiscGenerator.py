from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import math
from typing import List, Tuple, Dict
from datetime import datetime

from SkyMap import SkyMap
from Star import Star, ConstellationLines


class StarDiscGenerator:
    def __init__(
        self,
        diameter_inches: float = 8,
        center_hole_mm: float = 5,
        margin_inches: int = 1,
    ) -> None:
        self.diameter = diameter_inches * inch
        self.radius = self.diameter / 2
        self.center_hole = center_hole_mm / 25.4 * inch
        self.margin = margin_inches * inch

        self.page_width = self.diameter + (2 * self.margin)
        self.page_height = self.diameter + (2 * self.margin)

        self.center_x = self.page_width / 2
        self.center_y = self.page_height / 2

        self.constellation_lines = ConstellationLines.MAJOR_CONSTELLATIONS

    def create_disc_template(self, stars: List[Star], filename: str):
        c = canvas.Canvas(filename, pagesize=(self.page_width, self.page_height))

        # Draw alignment marks and center hole
        self._draw_disc_outline(c)
        self._draw_center_hole(c)
        self._draw_alignment_marks(c)

        sorted_stars = sorted(stars, key=lambda s: s.magnitude)
        brightest_stars = set(star.name for star in sorted_stars[:10])

        star_positions = {}

        # Convert and draw stars
        for star in sorted_stars:
            # Convert celestial coordinates to polar coordinates
            theta = (star.ra / 24.0) * 2 * math.pi

            r = self.radius * (90 - star.dec) / 90
            x = self.center_x + (r * math.cos(theta))
            y = self.center_y + (r * math.sin(theta))
            if hasattr(star, "hip"):
                star_positions[star.hip] = (x, y)

            self._draw_star(
                c,
                x,
                y,
                self._magnitude_to_size(star.magnitude),
                star.name,
                star.magnitude,
                draw_name=(star.hip if star.name in brightest_stars else None),
            )

        self._draw_constellation_lines(c, star_positions)

        c.save()

    def _draw_disc_outline(self, c: canvas.Canvas):
        # Draw outer circle centered on page
        c.setStrokeColorRGB(0, 0, 0)
        c.setDash([5, 5])
        c.circle(self.center_x, self.center_y, self.radius)

        # Draw diameter lines
        c.setDash([])
        # Horizontal diameter
        c.line(
            self.center_x - self.radius,
            self.center_y,
            self.center_x + self.radius,
            self.center_y,
        )
        # Vertical diameter
        c.line(
            self.center_x,
            self.center_y - self.radius,
            self.center_x,
            self.center_y + self.radius,
        )

    def _draw_center_hole(self, c: canvas.Canvas):
        c.setDash([])
        c.circle(self.center_x, self.center_y, self.center_hole / 2)

    def _draw_alignment_marks(self, c: canvas.Canvas):
        # Draw north marker and other alignment guides
        c.line(
            self.center_x,
            self.center_y + self.radius - 0.25 * inch,
            self.center_x,
            self.center_y + self.radius,
        )
        c.drawString(
            self.center_x - 0.1 * inch, self.center_y + self.radius - 0.2 * inch, "N"
        )

    def _draw_constellation_lines(
        self, c: canvas.Canvas, star_positions: Dict[int, Tuple[float, float]]
    ):
        """Draw constellation lines using stored star positions"""
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setLineWidth(0.5)

        for name, lines in self.constellation_lines.items():
            print(f"Drawing lines for {name}")
            for s1_hip, s2_hip in lines:
                if s1_hip in star_positions and s2_hip in star_positions:
                    x1, y1 = star_positions[s1_hip]
                    x2, y2 = star_positions[s2_hip]
                    c.line(x1, y1, x2, y2)
                    print(f"Drawing line from {x1}, {y1} to {x2}, {y2}")
                else:
                    print(f"Skipping line for {name} - missing star positions {s1_hip}, {s2_hip}")

    def _draw_star(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        size: float,
        name: str = None,
        magnitude: float = None,
        draw_name: bool = False,
    ):
        # Make sure coordinates are within bounds
        if 0 <= x <= self.diameter and 0 <= y <= self.diameter:
            c.setFillColorRGB(0, 0, 0)  # Black stars
            c.circle(x, y, size, stroke=0, fill=1)

            # Draw name for the brightest stars
            if draw_name and name:
                c.setFont("Helvetica", 6)  # Small font size
                # Position text below the star
                text_x = x - len(name) * 2  # Center text
                text_y = y - size - 8  # Place below star
                c.drawString(text_x, text_y, name)

    def _magnitude_to_size(self, magnitude):
        # Adjust size calculation - brighter stars should be bigger
        # Magnitude scale is inverse (smaller numbers are brighter)
        base_size = 2  # mm
        size = base_size * (1 / (magnitude + 2)) * inch / 25.4
        return min(size, 0.1 * inch)  # Cap maximum size


def generate_star_disc(lat: float, long: float, date_time: datetime = None):
    sky_map = SkyMap(lat, long)
    stars = sky_map.calculate_positions(date_time)

    generator = StarDiscGenerator()
    filename = f"star_disc_{datetime.now().strftime('%Y%m%d_%H')}.pdf"
    generator.create_disc_template(stars, filename)

    return filename
