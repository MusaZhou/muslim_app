from rest_framework import permissions

class ApproveAppPermission(permissions.BasePermission):
    message = 'Do not persist proper permissions'
    
    def has_permission(self, request, view):
        return request.user.has_perm('management.can_approve_app')