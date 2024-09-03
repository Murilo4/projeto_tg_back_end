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
from .views import get_user, user_manager, create_user, login_view

urlpatterns = [
    path('', get_user),
    path('create/', create_user, name='create_user'),
    path('login/', login_view, name='login'),
    path('user/<int:id>', user_manager, name='get_user'),
    path('update/', user_manager, name='update_user')
]