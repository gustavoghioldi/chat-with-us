from rest_framework.permissions import BasePermission

from tenants.models import TenantModel


class IsTenantAuthenticated(BasePermission):
    """
    Validates access based on cwu_token header.

    Checks if the cwu_token in request headers corresponds to a valid tenant.
    If valid, adds the tenant_id to request headers for use in views.
    """

    def has_permission(self, request, view):
        # Obtener el token del header
        cwu_token = request.headers.get("X-Cwu-Token")

        if not cwu_token:
            return False

        try:
            # Buscar el tenant por el token
            tenant = TenantModel.objects.get(cwu_token=cwu_token)

            # Agregar el tenant_id a los headers de la request para uso posterior
            if hasattr(request, "_request"):
                # Para DRF Request objects
                request._request.META["HTTP_TENANT_ID"] = str(tenant.id)
                request._request.META["HTTP_TENANT_NAME"] = tenant.name
            else:
                # Para Django Request objects
                request.META["HTTP_TENANT_ID"] = str(tenant.id)
                request.META["HTTP_TENANT_NAME"] = tenant.name

            # También agregar como atributo del request para fácil acceso
            request.tenant = tenant
            request.tenant_id = tenant.id

            return True

        except TenantModel.DoesNotExist:
            return False
