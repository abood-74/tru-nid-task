from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def _error_formatter(self, errors):
        formatted_errors = []
        for field, error in errors.items():
            for message in error:
                formatted_errors.append(
                    {
                        'field': field,
                        'message': message,
                    }
                )
        return formatted_errors