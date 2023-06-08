from rest_framework.permissions import BasePermission

class IsAdmin:
    def has_permission(self, request, view):
        if request.user.role.name_en == 'admin':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name_en == 'admin':
            return True
        return False


class IsSalesman:
    def has_permission(self, request, view):
        if request.user.role.name_en == 'salesman' or request.user.role.name_en == 'admin':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name_en == 'salesman' or request.user.role.name_en == 'admin':
            return True
        return False


class IsCustomer:
    def has_permission(self, request, view):
        if request.user.role.name_en == 'customer' or request.user.role.name_en == 'salesman' or \
                request.user.role.name_en == 'admin':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role.name_en == 'customer' or request.user.role.name_en == 'salesman' or \
                request.user.role.name_en \
                == \
                'admin':
            return True
        return False
