"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views.confirmation import confirmation_code, Verify_confirmation_code
from .views.confirmation import resend_email_code, validate_token_view
from .views.user_manager import user_account, user_delete, user_update
from .views.user_manager import user_password_update, verify_reset_token
from .views.create import create_user
from .views.login import login_view, logout_user, validate_session

urlpatterns = [
     path('login/', login_view,
          name='login'),
     path('user/<int:id>/', user_account,
          name='get_user'),
     path('user/update/<int:id>/', user_update,
          name='update_user'),
     path('send-user-data/', confirmation_code,
          name='send_user_data'),
     path('validate-token/', validate_token_view,
          name='validate_token_view'),
     path('verify-confirmation-code/', Verify_confirmation_code,
          name='verify_confirmation_code'),
     path('create/', create_user,
          name='create'),
     path('user/delete/<int:id>/', user_delete,
          name='user_delete'),
     path('user/reset-password/', user_password_update,
          name='user_password_update'),
     path('user/confirm-reset-password/', verify_reset_token,
          name='verify_reset_token'),
     path('resend-email/', resend_email_code,
          name='resend_email_code'),
     path('logout/', logout_user,
          name='logout'),
     path('validate-session/', validate_session,
          name='validate_session')
]
