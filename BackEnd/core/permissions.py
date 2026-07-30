from rest_framework import permissions


class EhDonoDoImovelOuSomenteLeitura(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.anfitriao_id == request.user.id


class EhAnfitriaoDaReserva(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.imovel.anfitriao_id == request.user.id


class EhHospedeDaReserva(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.hospede_id == request.user.id
