import ephem
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple
import math

from Star import Star, StarCatalog, ConstellationLines

class SkyMap:
    def __init__(self, lat: float, lon: float) -> None:
        self.obs = ephem.Observer()
        self.obs.lat = str(lat)
        self.obs.lon = str(lon)
        self.star_catalog = StarCatalog()

        self.stars = self._load_bright_stars()

    def _load_bright_stars(self) -> List[Star]:
        # We will start with bright starts (magnitude < 5)
        bright_stars = self.star_catalog.get_visible_stars(10)

        return bright_stars
    
    def calculate_positions(self, date_time: datetime = None) -> List[Star]:
        if date_time:
            self.obs.date = date_time
        else:
            self.obs.date = ephem.now()

        # Grab all the constellations and their lines
        constellations = ConstellationLines.MAJOR_CONSTELLATIONS.items()
        constellation_stars = []

        # Ensure we have the stars
        for constellation, star_ids in constellations:
            flat_star_ids = [star_id for star_id in star_ids]
            flat_star_ids = [star_id for sublist in flat_star_ids for star_id in sublist]
            stars = [star for star in self.stars if star.hip is not None and star.hip in flat_star_ids]
            constellation_stars.extend(stars)
            print(f"{constellation}: {len(stars)}")

        constellation_star_ids = [star.hip for star in constellation_stars]
        print(f"Constellation stars: {len(constellation_stars)}")



        # Calculate position for each star
        visible_stars = []
        for star in self.stars:
            fixed_body = ephem.FixedBody()
            fixed_body._ra = star.ra
            fixed_body._dec = star.dec
            fixed_body.compute(self.obs)

            # Convert alt/az to x/y coordinates
            az = float(fixed_body.az)
            alt = float(fixed_body.alt)

            # Only include stars above the horizon
            if alt > 0 or star.hip in [s for s in constellation_star_ids]:
                # Simple projection
                x = az * math.cos(alt)
                y = alt

                star.x = x
                star.y = y

                visible_stars.append(star)

        print(f"Visible stars: {len(visible_stars)}")
        return visible_stars