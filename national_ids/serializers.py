from rest_framework import serializers
from datetime import date

from core.base.serializers import BaseSerializer
from .constants import EGYPTIAN_GOVERNORATE_CODES


class EgyptianIDSerializer(BaseSerializer):
    """
    Serializer for validating Egyptian national IDs.
    """
    national_id = serializers.CharField(max_length=14, min_length=14)
    
    GOVERNORATE_CODES = EGYPTIAN_GOVERNORATE_CODES
    VALID_CENTURIES_DIGITS = [2, 3]


    def validate_national_id(self, value):
        """
        Main validation method that orchestrates all validations.
        """
        
        if not isinstance(value, str):
            raise serializers.ValidationError("ID value must be a string")
        
        if not value.isdigit():
            raise serializers.ValidationError("ID value must be digits only")
        
        self._validate_century(value)
        self._validate_year(value)
        self._validate_month(value)
        self._validate_day(value)
        self._validate_date_of_birth(value)
        self._validate_governorate(value)
        
        return value

    def _validate_century(self, id_value):
        """Validate century digit (first digit)"""
        century_digit = int(id_value[0])
        if century_digit not in self.VALID_CENTURIES_DIGITS:
            raise serializers.ValidationError("Invalid century digit")

    def _validate_year(self, id_value):
        """Validate year (second and third digits)"""
        century = int(id_value[0])
        year_part = int(id_value[1:3])
        full_year = (1900 if century == 2 else 2000) + year_part
        
        if full_year > date.today().year:
            raise serializers.ValidationError("Invalid year")

    def _validate_month(self, id_value):
        """Validate month (fourth and fifth digits)"""
        month = int(id_value[3:5])
        if month not in range(1, 13):
            raise serializers.ValidationError("Invalid month")

    def _validate_day(self, id_value):
        """Validate day (sixth and seventh digits)"""
        day = int(id_value[5:7])
        if day not in range(1, 32):
            raise serializers.ValidationError("Invalid day")

    def _validate_date_of_birth(self, id_value):
        """Validate the complete date of birth (year, month, day)"""
        try:
            century = int(id_value[0])
            year = (1900 if century == 2 else 2000) + int(id_value[1:3])
            month = int(id_value[3:5])
            day = int(id_value[5:7])
            
            date_of_birth = date(year, month, day)
            if date_of_birth > date.today():
                raise serializers.ValidationError("Invalid date of birth")
        except ValueError:
            raise serializers.ValidationError("Invalid date of birth")

    def _validate_governorate(self, id_value):
        """Validate governorate code (eighth and ninth digits)"""
        governorate_code = id_value[7:9]
        if governorate_code not in self.GOVERNORATE_CODES:
            raise serializers.ValidationError("Invalid governorate code")