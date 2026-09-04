from django.db import migrations


def create_moderator_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='Moderator')

    # Product-related — full CRUD
    product_app_models = ['product', 'productvariant', 'attributevalue', 'attributetype', 'category']
    # Order-related — shudhu dekha ar status change, delete na (customer order delete kora uchit na)
    order_only_models = ['order']

    codenames = []
    for model in product_app_models:
        codenames += [f'add_{model}', f'change_{model}', f'delete_{model}', f'view_{model}']
    for model in order_only_models:
        codenames += [f'change_{model}', f'view_{model}']

    permissions = Permission.objects.filter(codename__in=codenames)
    group.permissions.set(permissions)


def remove_moderator_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Moderator').delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
        # NOTE: ei migration Product, Category, Order app er model gula toiri
        # howar POR e chalate hobe, tai neeche manually dependency add kore dao
        # e.g. ('Product', '0001_initial'), ('Category', '0001_initial'), ('Order', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_moderator_group, remove_moderator_group),
    ]
