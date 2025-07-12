from rest_framework import status
from rest_framework.views import APIView

class UnifiedResponseMixin:
    """
    Mixin to format responses for all views, providing a consistent
    API structure with 'success', 'message', 'data', and 'errors' fields.
    """

    def format_response(self, response, success_message, error_message):
        is_success = response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_202_ACCEPTED,
        ]
        response.data = {
            'success': is_success,
            'message': success_message if is_success else error_message,
            'data': response.data if is_success else None,
            'errors': response.data if not is_success else None,
        }
        return response

class UnifiedResponseAPIView(UnifiedResponseMixin, APIView):
    success_message = 'Operation completed successfully'
    error_message = 'Operation failed'
    
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        return self.format_response(
            response, 
            success_message=self.success_message, 
            error_message=self.error_message
        )