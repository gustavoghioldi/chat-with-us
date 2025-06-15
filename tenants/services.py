from tenants.models import TenantModel


class TenantService:

    @staticmethod
    def create(tenant_data):
        tenant = TenantModel(**tenant_data)
        tenant.save()
        return tenant
