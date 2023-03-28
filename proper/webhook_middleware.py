import hmac
import hashlib
import base64
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings

class WebhookSignatureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        signature = request.headers.get('verif-hash')
        if signature is None:
            return HttpResponseBadRequest()

        signature_parts = signature.split('.')
        if len(signature_parts) != 2:
            return HttpResponseBadRequest()

        secret_key = settings.FLUTTERWAVE_SECRET_KEY
        message = request.body
        expected_signature = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256)
        expected_signature = base64.b64encode(expected_signature.digest()).decode('utf-8')

        if not hmac.compare_digest(signature_parts[1], expected_signature):
            return HttpResponseForbidden()

        response = self.get_response(request)
        return response
