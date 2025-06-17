"""
Middleware para manejo de tenant basado en cwu_token.

Este middleware extrae el tenant de los headers y lo hace disponible
a través de thread-local storage para usar en toda la aplicación.
"""

import threading

from django.utils.deprecation import MiddlewareMixin

from tenants.models import TenantModel

# Thread-local storage para el tenant actual
_thread_locals = threading.local()


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que extrae y almacena el tenant actual basado en cwu_token.

    Permite acceder al tenant desde cualquier parte del código usando:
    from api.middleware.tenant_middleware import get_current_tenant
    tenant = get_current_tenant()
    """

    def process_request(self, request):
        # Limpiar el tenant anterior
        _thread_locals.tenant = None

        # Obtener el token del header
        cwu_token = request.headers.get("cwu_token") or request.headers.get("Cwu-Token")

        if cwu_token:
            try:
                tenant = TenantModel.objects.get(cwu_token=cwu_token)
                _thread_locals.tenant = tenant

                # Agregar al request para compatibilidad
                request.tenant = tenant
                request.tenant_id = tenant.id

            except TenantModel.DoesNotExist:
                pass

    def process_response(self, request, response):
        # Limpiar al final de la request
        _thread_locals.tenant = None
        return response


def get_current_tenant():
    """
    Obtiene el tenant actual de la request.

    Returns:
        TenantModel or None: El tenant actual o None si no hay uno válido
    """
    return getattr(_thread_locals, "tenant", None)


def get_current_tenant_id():
    """
    Obtiene el ID del tenant actual.

    Returns:
        int or None: El ID del tenant actual o None si no hay uno válido
    """
    tenant = get_current_tenant()
    return tenant.id if tenant else None
