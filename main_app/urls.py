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
from .views import user_manager, create_user, login_view, get_home, confirmation_code, VerifyConfirmationCodeView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('user/<int:id>/', user_manager, name='get_user'),
    path('user/update/', user_manager, name='update_user'),
    path('create/', create_user, name='create_user'),
    path('send-confirmation-code/', confirmation_code, name='send-confirmation-code'),
    path('verify-confirmation-code/', VerifyConfirmationCodeView.as_view(), name='verify-confirmation-code'),
    path('delete/<int:id>', user_manager, name='delete_user'),
    path('', get_home, name='home'),
]