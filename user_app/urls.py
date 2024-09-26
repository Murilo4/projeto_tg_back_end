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
from .views.user_manager import user_account, user_delete, user_update, user_password_update, reset_password
from .views.create import create_user
from .views.login import login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('user/<int:id>/', user_account, name='get_user'),
    path('user/update/', user_update, name='update_user'),
    path('create/', create_user, name='create_user'),
    path('send-email/', confirmation_code, name='send-confirmation-code'),
    path('verify-confirmation-code/', Verify_confirmation_code, name='verify-confirmation-code'),
    path('delete/<int:id>', user_delete, name='delete_user'),
    path('user/reset-password/', user_password_update, name='user_password_update'),
    path('user/confirm-reset-password/', reset_password, name='reset_password')
]