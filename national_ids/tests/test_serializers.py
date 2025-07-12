import pytest
from rest_framework import serializers
from national_ids.serializers import EgyptianIDSerializer


class TestEgyptianIDSerializer:

    def test_valid_egyptian_id(self):
        serializer = EgyptianIDSerializer(data={'national_id': '29001010123456'})
        assert serializer.is_valid()

    def test_invalid_length_short(self):
        serializer = EgyptianIDSerializer(data={'national_id': '2900101012345'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_invalid_length_long(self):
        serializer = EgyptianIDSerializer(data={'national_id': '290010101234567'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_non_digit_characters(self):
        serializer = EgyptianIDSerializer(data={'national_id': '2900101012345a'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_invalid_century_digit(self):
        serializer = EgyptianIDSerializer(data={'national_id': '19001010123456'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_invalid_month(self):
        serializer = EgyptianIDSerializer(data={'national_id': '29013010123456'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_invalid_day(self):
        serializer = EgyptianIDSerializer(data={'national_id': '29001332123456'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_invalid_governorate_code(self):
        serializer = EgyptianIDSerializer(data={'national_id': '29001099123456'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_future_date(self):
        serializer = EgyptianIDSerializer(data={'national_id': '32601010123456'})
        assert not serializer.is_valid()
        assert 'national_id' in serializer.errors

    def test_valid_governorate_codes(self):
        valid_codes = ['01', '02', '11', '21', '88']
        for code in valid_codes:
            id_value = f'2900101{code}23456'
            serializer = EgyptianIDSerializer(data={'national_id': id_value})
            assert serializer.is_valid(), f"Failed for governorate code {code}. Errors: {serializer.errors}" 