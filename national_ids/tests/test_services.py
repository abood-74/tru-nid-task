import pytest
from datetime import date
from national_ids.services import EgyptianIDExtractor


class TestEgyptianIDExtractor:

    def test_extract_date_of_birth(self):
        extractor = EgyptianIDExtractor('29001010123456')
        assert extractor._extract_date_of_birth() == date(1990, 1, 1)

    def test_extract_century_2000s(self):
        extractor = EgyptianIDExtractor('30001011234567')
        assert extractor._extract_century() == 3

    def test_extract_century_1900s(self):
        extractor = EgyptianIDExtractor('29001010123456')
        assert extractor._extract_century() == 2

    def test_extract_year_1900s(self):
        extractor = EgyptianIDExtractor('29001010123456')
        assert extractor._extract_year() == 1990

    def test_extract_year_2000s(self):
        extractor = EgyptianIDExtractor('30001011234567')
        assert extractor._extract_year() == 2000

    def test_extract_month(self):
        extractor = EgyptianIDExtractor('29012011234567')
        assert extractor._extract_month() == 12

    def test_extract_day(self):
        extractor = EgyptianIDExtractor('29001231234567')
        assert extractor._extract_day() == 23

    def test_extract_governorate_cairo(self):
        extractor = EgyptianIDExtractor('29001010123456')
        assert extractor._extract_governorate() == 'Cairo'

    def test_extract_governorate_alexandria(self):
        extractor = EgyptianIDExtractor('29001020234567')
        assert extractor._extract_governorate() == 'Alexandria'

    def test_extract_governorate_unknown(self):
        extractor = EgyptianIDExtractor('29001099234567')
        assert extractor._extract_governorate() == 'Unknown'

    def test_extract_gender_male(self):
        extractor = EgyptianIDExtractor('29001010123456')
        assert extractor._extract_gender() == 'male'

    def test_extract_gender_female(self):
        extractor = EgyptianIDExtractor('29001010123464')
        assert extractor._extract_gender() == 'female'

    def test_get_data_complete(self):
        extractor = EgyptianIDExtractor('29001010123456')
        data = extractor.get_data()
        
        assert data['national_id'] == '29001010123456'
        assert data['date_of_birth'] == date(1990, 1, 1)
        assert data['governorate'] == 'Cairo'
        assert data['gender'] == 'male'
        assert len(data) == 4 