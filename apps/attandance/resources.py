from import_export import resources
from .models import CustomUser
from import_export.fields import Field
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserResource(resources.ModelResource):
    ins_groups = Field(attribute='ins_groups', column_name='Biriktish kerak bo\'lgan Guruh')
    groups = Field(attribute='groups', column_name='Role')

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'ins_groups', 'groups', 'password')
        export_order = ('id', 'username', 'email', 'first_name', 'last_name', 'ins_groups', 'groups')
        formats = ['xls', 'xlsx', 'csv', 'json', 'html', 'tsv']

    def dehydrate_ins_groups(self, user):
        return user.ins_groups.name if user.ins_groups else ''

    def dehydrate_groups(self, user):
        return ', '.join([group.name for group in user.groups.all()])

    def before_import_row(self, row, **kwargs):

        if 'Role' in row:
            group_names = row['Role'].split(',')
            groups = []
            for name in group_names:
                group = User.groups.model.objects.filter(name=name.strip()).first()
                if group:
                    groups.append(group.id)
            row['Role'] = ','.join(map(str, groups))

    def after_import_row(self, row, **kwargs):
        pass
