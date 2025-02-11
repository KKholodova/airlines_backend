from rest_framework.permissions import BasePermission

from app.utils import identity_user


class IsAuthenticated(BasePermission): #Проверяет, что пользователь авторизован
    def has_permission(self, request, view):
        user = identity_user(request)

        if user is None:
            return False

        return user.is_active


class IsModerator(BasePermission): #Проверяет, что у пользователя есть права модератора
    def has_permission(self, request, view):
        user = identity_user(request)

        if user is None:
            return False

        return user.is_superuser
