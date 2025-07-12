# core/base/national_id_extractors.py
import abc
from functools import wraps
from typing import Dict, Any, Optional


class BaseIDExtractor(metaclass=abc.ABCMeta):
    """
    Base ID Extractor class for data extraction only.
    Focuses purely on extraction without validation concerns.
    """
    
    def __init__(self, id_value: str):
        self.id_value = id_value
    
    @abc.abstractmethod
    def _extract_century(self) -> int:
        """Extract century from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_year(self) -> int:
        """Extract full year from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_month(self) -> int:
        """Extract month from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_day(self) -> int:
        """Extract day from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_date_of_birth(self):
        """Extract complete date of birth from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_governorate(self) -> str:
        """Extract governorate from ID"""
        pass
    
    @abc.abstractmethod
    def _extract_gender(self) -> str:
        """Extract gender from ID"""
        pass
    
    @abc.abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Extract all data from ID and return as dictionary"""
        pass