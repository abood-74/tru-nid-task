from core.base.national_id_extractors import BaseIDExtractor
from .constants import EGYPTIAN_GOVERNORATE_CODES
from datetime import date
from typing import Dict, Any

class EgyptianIDExtractor(BaseIDExtractor):
    GOVERNORATE_CODES = EGYPTIAN_GOVERNORATE_CODES

    def _extract_century(self) -> int:
        """Extract century from ID (first digit)"""
        return int(self.id_value[0])

    def _extract_year(self) -> int:
        """Extract full year from ID (second and third digits)"""
        century = self._extract_century()
        year_part = int(self.id_value[1:3])
        return (1900 if century == 2 else 2000) + year_part

    def _extract_month(self) -> int:
        """Extract month from ID (fourth and fifth digits)"""
        return int(self.id_value[3:5])

    def _extract_day(self) -> int:
        """Extract day from ID (sixth and seventh digits)"""
        return int(self.id_value[5:7])

    def _extract_date_of_birth(self) -> date:
        """Extract complete date of birth from ID (year, month, day)"""
        return date(self._extract_year(), self._extract_month(), self._extract_day())

    def _extract_governorate(self) -> str:
        """Extract governorate from ID (eighth and ninth digits)"""
        governorate_code = self.id_value[7:9]
        return self.GOVERNORATE_CODES.get(governorate_code, "Unknown")

    def _extract_gender(self) -> str:
        """Extract gender from ID (eleventh digit)"""
        return "male" if int(self.id_value[12]) % 2 != 0 else "female"

    def get_data(self) -> Dict[str, Any]:
        """Extract all data from ID (date of birth, governorate, gender)"""
        return {
            "national_id": self.id_value,
            "date_of_birth": self._extract_date_of_birth(),
            "governorate": self._extract_governorate(),
            "gender": self._extract_gender(),
        }
