import ephem
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import requests
from pathlib import Path
import csv

HYG_DATA_URL = "https://raw.githubusercontent.com/astronexus/HYG-Database/refs/heads/main/hyg/CURRENT/hygdata_v41.csv"


@dataclass
class Star:
    id: int
    name: str
    magnitude: float
    ra: float  # Right Ascension
    dec: float  # Declination
    x: float = 0
    y: float = 0
    constellation: Optional[str] = None
    common_name: Optional[str] = None
    hip: Optional[int] = None


class StarCatalog:
    def __init__(self) -> None:
        self.stars: Dict[int, Star] = {}
        self.bright_star_threshold = 4.5
        self._load_catalog()

    def _download_catalog(self):
        """Download star catalog if not present"""
        catalog_path = Path("data/hygdata_v41.csv")
        if not catalog_path.exists():
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(HYG_DATA_URL)
            with catalog_path.open("wb") as f:
                f.write(response.content)
        return catalog_path

    def _load_catalog(self):
        """Loads and parses star catalog"""
        catalog_path = self._download_catalog()

        with open(catalog_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Only include stars brighter than threshold
                    magnitude = float(row["mag"])
                    if magnitude <= self.bright_star_threshold:
                        star = Star(
                            id=int(row["id"]),
                            name=(
                                row["proper"] or f"HIP {row['hip']}"
                                if row["hip"]
                                else f"HD {row['hd']}"
                            ),
                            magnitude=magnitude,
                            ra=float(row["ra"]),
                            dec=float(row["dec"]),
                            constellation=row["con"],
                            common_name=row["proper"] if row["proper"] else None,
                            hip=int(row["hip"]) if row["hip"] else None,
                        )
                        self.stars[star.id] = star
                except (ValueError, KeyError) as e:
                    continue

    def get_visible_stars(self, magnitude_limit: float = None) -> List[Star]:
        """Returns list of stars brighter than specified magnitude"""
        if magnitude_limit is None:
            magnitude_limit = self.bright_star_threshold

        return [
            star for star in self.stars.values() if star.magnitude <= magnitude_limit
        ]

    def get_constellation_stars(self, constellation: str) -> List[Star]:
        """Returns list of stars in specified constellation"""
        return [
            star
            for star in self.stars.values()
            if star.constellation
            and star.constellation.upper() == constellation.upper()
        ]

    def get_named_stars(self) -> List[Star]:
        """Returns list of stars with common names"""
        return [star for star in self.stars.values() if star.common_name]


class ConstellationLines:
    MAJOR_CONSTELLATIONS = {
        "Orion": [
            (26727, 26311),  # Betelgeuse to Bellatrix
            (26311, 25930),  # Bellatrix to Mintaka
            (25930, 26727),  # Mintaka to Alnilam
            (26727, 27366),  # Alnilam to Alnitak
            (27366, 27989),  # Alnitak to Saiph
            (27989, 29426),  # Saiph to Rigel
            (29426, 25930),  # Rigel to Mintaka
        ],
        "Taurus": [
            (25428, 26451),  # Aldebaran to Ain (Hyades cluster)
            (26451, 27913),  # Ain to Hyadum I
            (27913, 28380),  # Hyadum I to Chamukuy
            (28380, 29434),  # Chamukuy to Alcyone (Pleiades cluster)
            (29434, 32349),  # Alcyone to Atlas
            (32349, 31681),  # Atlas to Electra
        ],
        "Gemini": [
            (31637, 30343),  # Castor to Pollux
            (30343, 29655),  # Pollux to Wasat
            (29655, 28910),  # Wasat to Mekbuda
            (28910, 28734),  # Mekbuda to Alhena
            (28734, 27673),  # Alhena to Tejat Posterior
        ],
        "Auriga": [
            (24608, 28380),  # Capella to Menkalinan
            (28380, 28360),  # Menkalinan to Mahasim
            (28360, 25428),  # Mahasim to Elnath (shared with Taurus)
            (25428, 24608),  # Elnath to Capella
        ],
        "Canis Major": [
            (32349, 33165),  # Sirius to Mirzam
            (33165, 34444),  # Mirzam to Aludra
            (34444, 33579),  # Aludra to Wezen
            (33579, 32349),  # Wezen to Sirius
        ],
        "Ursa Major": [
            (54061, 53910),  # Dubhe to Merak
            (53910, 58001),  # Merak to Phecda
            (58001, 59774),  # Phecda to Megrez
            (59774, 65378),  # Megrez to Alioth
            (65378, 67301),  # Alioth to Mizar
            (67301, 68127),  # Mizar to Alkaid
        ],
        "Perseus": [
            (15863, 14576),  # Mirfak to Algol
            (15863, 13654),  # Mirfak to Atik
            (13654, 13268),  # Atik to Menkib
            (13268, 14576),  # Menkib to Algol
        ],
        "Cancer": [
            (44066, 42911),  # Acubens to Asellus Australis
            (42911, 42806),  # Asellus Australis to Asellus Borealis
            (42806, 41909),  # Asellus Borealis to Tegmine
        ],
    }
