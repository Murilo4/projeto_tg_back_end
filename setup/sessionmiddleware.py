from django.http import JsonResponse
from rest_framework import status
from functools import wraps


def require_session_id(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('token')
        if token is None or token == "":
            return JsonResponse({
                                "success": False,
                                "message": f"sessão não encontrada{token}"},
                                status=status.HTTP_404_NOT_FOUND)
        # Verificar se o token ainda existe armazenado no cookie
        if 'session_id' not in request.COOKIES or request.COOKIES['session_id'] == "" or request.COOKIES['session_id'] is None:
            return JsonResponse({
                                "success": False,
                                "message": "sessão não encontrada"},
                                status=status.HTTP_404_NOT_FOUND)
        return view_func(request, *args, **kwargs)
    return wrapper
