from rest_framework import status
from ..models import User
from rest_framework.response import Response
from ..serializers import UserSerializer, UserChangeSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.mail import EmailMultiAlternatives
from setup.settings import EMAIL_HOST_USER
from django.http import HttpResponseNotFound
from ..serializers import UserGetSerializer
import requests
from ..code_and_security.code_generator import make_custom_token, validate_jwt
from django.views.decorators.csrf import csrf_exempt
import os


@csrf_exempt
@api_view(['GET'])
def user_account(request):
    if request.method == 'GET':
        try:

            token = request.headers.get('Authorization')

            jwt_data = validate_jwt(token)
            if not jwt_data:
                return Response({"success": False,
                                 "message": "token Invalido"},
                                status=status.HTTP_401_UNAUTHORIZED)

            user_id = jwt_data.get('id')

            user = User.objects.get(id=user_id)
            serializer = UserGetSerializer(user)
            user_data = {
                "email": serializer.data.get("email"),
                "name": serializer.data.get("user_name"),
                "nickname": serializer.data.get("nick_name"),
                "phone": serializer.data.get("phone_number"),
                "photo": serializer.data.get("user_img")
            }
            return JsonResponse({
                "success": True,
                "message": ["Usuário encontrado"],
                "data": user_data},
                status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": ["Usuário não foi encontrado"]},
                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Imprimir o erro para debugging
            print("Erro:", str(e))
            return JsonResponse({
                "success": False,
                "message": ["Não foi possível validar o usuário", str(e)]},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return JsonResponse({"success": False,
                             "message": ["Metodo não autorizado"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['DELETE'])
def user_delete(request):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')

            jwt_data = validate_jwt(token)
            if not jwt_data:
                return JsonResponse({"success": False,
                                     "message": ["Token inválido"]},
                                    status=status.HTTP_401_UNAUTHORIZED)

            user_id = jwt_data.get('id')

            decks_url = f"{os.getenv('DECK_URL')}/get-all-decks-to-user/{user_id}/"
            response = requests.get(decks_url)
            if response.status_code == 200:
                decks = response.json()
                for deck in decks:
                    deck_id = deck['id']

                    delete_deck_url = f"{os.getenv('DECK_URL')}/delete-deck/{deck_id}/"
                    delete_deck_response = requests.delete(
                        delete_deck_url, headers={"Authorization": token})
                    if delete_deck_response.status_code != 200:
                        return JsonResponse({
                            "success": False,
                            "message": [f"Falha ao deletar o deck {deck_id}."]
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return JsonResponse({
                    "success": False,
                    "message": ["Falha ao recuperar os decks do usuário."]
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user = User.objects.get(id=user_id)
            user.delete()

            return JsonResponse({
                "success": True,
                "message": ["Usuário deletado com sucesso."]
            }, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": ["Usuário não encontrado."]
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({
        "success": False,
        "message": ["Método não permitido."]
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['PUT'])
def user_update(request):
    if request.method == 'PUT':
        try:
            # Extract the JWT token from the request header
            token = request.headers.get('Authorization')

            # Validate the token and get user data
            jwt_data = validate_jwt(token)
            user_id = jwt_data.get('id')
            user = User.objects.get(id=user_id)

            if user:
                errors = []

                # Get the new email and nickname from request data
                email = request.data.get('email')
                nickname = request.data.get('nickname')

                # Check if nickname already exists for another user
                if User.objects.filter(nick_name=nickname).exclude(pk=user_id).exists():
                    errors.append("Usuário com este apelido já existe")

                # Check if email is already registered
                if User.objects.filter(email=email).exclude(pk=user_id).exists():
                    errors.append("Email já está registrado")

                # Return validation errors if any
                if errors:
                    return JsonResponse({
                        "success": False,
                        "message": errors
                    }, status=status.HTTP_400_BAD_REQUEST)

                # If the email hasn't changed, proceed with updating the user
                if email == user.email:
                    # Update user data using the serializer
                    serializer = UserChangeSerializer(user, data=request.data, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({
                            "data": serializer.data,
                            "success": True,
                            "message": ["Usuário atualizado com sucesso"]
                        }, status=status.HTTP_202_ACCEPTED)

        except ValidationError as e:
            # Handle the ValidationError and return it as a serializable response
            return Response({
                "success": False,
                "message": list(e.args)  # Convert ValidationError messages to a list of strings
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # Handle case where the user doesn't exist in the database
            return JsonResponse({
                "success": False,
                "message": ["Usuário não encontrado"]
            }, status=status.HTTP_404_NOT_FOUND)

    else:
        return JsonResponse({
            "success": False,
            "message": ["Método não autorizado"]
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def user_password_update(request):
    if request.method == "POST":
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": ["Email não encontrado"]},
                status=status.HTTP_404_NOT_FOUND)
        # Gerar o token e enviar o email
        send_reset_email(user)
        return Response({
            "success": True,
            "message": ["enviando email"]},
            status=status.HTTP_200_OK)
    else:
        return JsonResponse({"success": False,
                             "message": ["Metódo não autorizado"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


def send_reset_email(user):
    token = make_custom_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"https://flashvibe.onrender.com/redefinir-senha?uid={uid}&token={token}"

    subject = "Flash vibe "
    html_message = (f"""
        <p style="font-size:20px; color: #000;">Segue o link para redefinição
        de senha, se você não solicitou a troca de senha,
        desconsidere este link</p>
        <p style="display: inline-block;">
        <a href="{link}" style="background-color: #7fcfff;
        padding: 10px; border-radius: 5px; font-size: 24px;
        text-decoration: none; color: #000;">
            <strong>Redefinir Senha</strong>
            </a>
        </p>
        <p style="font-size:20px; color: #000;">Qualquer
        dúvida, entre em contato conosco.</p>
        """
    )
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=html_message,
        from_email=EMAIL_HOST_USER,
        to=[user.email],
    )
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()
    return Response({
        "success": True,
        "message": ["email enviado com sucesso"]},
        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def verify_reset_token(request):
    if request.method == "POST":
        uidb64 = request.data.get('uid')
        token = request.data.get('token')

        # Verifica se o token é válido
        if is_valid_token(uidb64, token):
            return Response({
                "success": True,
                "message": ["Token válido"]},
                status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": ["Token inválido ou expirado!"]},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"success": False,
                             "message": ["Método não permitido"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


def is_valid_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return False

    if (default_token_generator.check_token(user, token)):
        return Response({
            "success": True,
            "message": ["Código verificado com sucesso"]},
            status=status.HTTP_200_OK)
