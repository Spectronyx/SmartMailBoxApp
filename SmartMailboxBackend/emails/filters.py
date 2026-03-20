from django_filters import rest_framework as filters
from .models import Email

class EmailFilter(filters.FilterSet):
    """
    Advanced filter set for Emails.
    
    Supports:
    - Date range filtering on received_at
    - Filtering by mailbox
    - Filtering by category
    - Filtering by sender (exact or contains)
    - Filtering by attachment presence
    """
    
    received_at_after = filters.DateTimeFilter(field_name='received_at', lookup_expr='gte')
    received_at_before = filters.DateTimeFilter(field_name='received_at', lookup_expr='lte')
    
    has_attachments = filters.BooleanFilter(method='filter_has_attachments')
    
    class Meta:
        model = Email
        fields = ['mailbox', 'category', 'sender']

    def filter_has_attachments(self, queryset, name, value):
        if value is True:
            return queryset.filter(attachments__isnull=False).distinct()
        elif value is False:
            return queryset.filter(attachments__isnull=True)
        return queryset
