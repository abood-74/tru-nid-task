import logging
from django.db import transaction
from django.utils import timezone
from national_ids.services import EgyptianIDExtractor
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from users.models import APIUsage
from core.base.views import UnifiedResponseAPIView
from national_ids.serializers import EgyptianIDSerializer
from core.utils.custom_throttles import EgyptianIDThrottle

logger = logging.getLogger(__name__)

class EgyptianIDExtractorAPIView(UnifiedResponseAPIView):
    success_message = 'ID validation completed successfully'
    error_message = 'ID validation failed'
    throttle_classes = [EgyptianIDThrottle]
    
    def post(self, request):
        try:
            with transaction.atomic():
                user = request.user
                
                if not user.has_sufficient_tokens(1):
                    self._log_usage(request, 0, status.HTTP_402_PAYMENT_REQUIRED)
                    return Response(
                        {
                            "success": False,
                            "message": "Insufficient tokens",
                            "data": None,
                            "errors": [{"detail": "Not enough tokens to process this request"}]
                        },
                        status=status.HTTP_402_PAYMENT_REQUIRED
                    )
                
                serializer = EgyptianIDSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                id_value = serializer.validated_data['national_id']
                extractor = EgyptianIDExtractor(id_value)
                extracted_data = extractor.get_data()
                
                self._log_usage(request, 1, status.HTTP_200_OK)
                user.deduct_tokens(1)
                
                return Response(extracted_data, status=status.HTTP_200_OK)
                
        except ValidationError as e:
            self._log_usage(request, 0, status.HTTP_400_BAD_REQUEST)
            return Response(
                serializer._error_formatter(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            self._log_usage(request, 0, status.HTTP_500_INTERNAL_SERVER_ERROR)
            logger.error(f"Error extracting ID: {e}")
            return Response(
                {
                    "success": False,
                    "message": str(e),
                    "data": None,
                    "errors": [str(e)]
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def _log_usage(self, request: Request, tokens_used: int, response_status: int) -> None:
        """Log API usage for tracking and billing purposes."""
        try:
            api_key = getattr(request, 'auth', None)
            APIUsage.objects.create(
                api_key=api_key,
                ip_address=self._get_client_ip(request),
                user_agent=self._get_user_agent(request),
                tokens_used=tokens_used,
                response_status=str(response_status),
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")
    
    def _get_client_ip(self, request: Request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()
        
        return request.META.get('REMOTE_ADDR', 'Unknown')
    
    def _get_user_agent(self, request: Request) -> str:
        return request.META.get('HTTP_USER_AGENT', 'Unknown')
    
