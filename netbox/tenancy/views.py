from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from circuits.models import Circuit
from dcim.models import Site, Rack, Device
from ipam.models import IPAddress, Prefix, VLAN, VRF
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)

from models import Tenant, TenantGroup
from . import filters, forms, tables


#
# Tenant groups
#

class TenantGroupListView(ObjectListView):
    queryset = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    table = tables.TenantGroupTable
    edit_permissions = ['tenancy.change_tenantgroup', 'tenancy.delete_tenantgroup']
    template_name = 'tenancy/tenantgroup_list.html'


class TenantGroupEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.change_tenantgroup'
    model = TenantGroup
    form_class = forms.TenantGroupForm
    obj_list_url = 'tenancy:tenantgroup_list'
    use_obj_view = False


class TenantGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenantgroup'
    cls = TenantGroup
    default_redirect_url = 'tenancy:tenantgroup_list'


#
#  Tenants
#

class TenantListView(ObjectListView):
    queryset = Tenant.objects.select_related('group')
    filter = filters.TenantFilter
    filter_form = forms.TenantFilterForm
    table = tables.TenantTable
    edit_permissions = ['tenancy.change_tenant', 'tenancy.delete_tenant']
    template_name = 'tenancy/tenant_list.html'


def tenant(request, slug):

    tenant = get_object_or_404(Tenant, slug=slug)
    stats = {
        'site_count': Site.objects.filter(tenant=tenant).count(),
        'rack_count': Rack.objects.filter(tenant=tenant).count(),
        'device_count': Device.objects.filter(tenant=tenant).count(),
        'vrf_count': VRF.objects.filter(tenant=tenant).count(),
        'prefix_count': Prefix.objects.filter(
            Q(tenant=tenant) |
            Q(tenant__isnull=True, vrf__tenant=tenant)
        ).count(),
        'ipaddress_count': IPAddress.objects.filter(
            Q(tenant=tenant) |
            Q(tenant__isnull=True, vrf__tenant=tenant)
        ).count(),
        'vlan_count': VLAN.objects.filter(tenant=tenant).count(),
        'circuit_count': Circuit.objects.filter(tenant=tenant).count(),
    }

    return render(request, 'tenancy/tenant.html', {
        'tenant': tenant,
        'stats': stats,
    })


class TenantEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.change_tenant'
    model = Tenant
    form_class = forms.TenantForm
    fields_initial = ['group']
    template_name = 'tenancy/tenant_edit.html'
    obj_list_url = 'tenancy:tenant_list'


class TenantDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'tenancy.delete_tenant'
    model = Tenant
    redirect_url = 'tenancy:tenant_list'


class TenantBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'tenancy.add_tenant'
    form = forms.TenantImportForm
    table = tables.TenantTable
    template_name = 'tenancy/tenant_import.html'
    obj_list_url = 'tenancy:tenant_list'


class TenantBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'tenancy.change_tenant'
    cls = Tenant
    form = forms.TenantBulkEditForm
    template_name = 'tenancy/tenant_bulk_edit.html'
    default_redirect_url = 'tenancy:tenant_list'


class TenantBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenant'
    cls = Tenant
    default_redirect_url = 'tenancy:tenant_list'
