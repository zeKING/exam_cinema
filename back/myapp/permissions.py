from rest_framework.permissions import BasePermission

class IsAdmin:
    def has_permission(self, request, view):
        if request.user.role.name_en == 'admin':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == 'admin':
            return True
        return False


class IsSalesman:
    def has_permission(self, request, view):
        if request.user.role.name == 'Продавец' or request.user.role.name == 'Администратор' :
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == 'Продавец' or request.user.role.name == 'Администратор':
            return True
        return False


class IsCustomer:
    def has_permission(self, request, view):
        if request.user.role.name == 'Покупатель' or request.user.role.name == 'Продавец' or request.user.role.name == \
                'Администратор':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name == 'Покупатель' or request.user.role.name == 'Продавец' or request.user.role.name == \
                'Администратор':
            return True
        return False
