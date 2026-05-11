from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.migrations import RunPython


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Observer — только просмотр
    observer, _ = Group.objects.get_or_create(name="observer")

    # Manager — полный доступ к товарам, партиям, складам, поставщикам
    manager, _ = Group.objects.get_or_create(name="manager")

    # Права для manager
    models_perms = [
        ("Products", "product"),
        ("Categories", "category"),
        ("Warehouses", "warehouse"),
        ("Suppliers", "supplier"),
        ("Batches", "batch"),
    ]

    # Права на добавление/изменение/удаление для менеджера
    manager_perms = []
    for model_name, codename in models_perms:
        ct = ContentType.objects.filter(
            app_label="sklad_logic", model=model_name.lower()
        ).first()
        if ct:
            for action in ("add", "change", "delete", "view"):
                perm = Permission.objects.filter(
                    codename=f"{action}_{codename}", content_type=ct
                ).first()
                if perm:
                    manager_perms.append(perm)

    manager.permissions.add(*manager_perms)

    # Observer — только view права на всё
    observer_perms = []
    for model_name, codename in models_perms:
        ct = ContentType.objects.filter(
            app_label="sklad_logic", model=model_name.lower()
        ).first()
        if ct:
            perm = Permission.objects.filter(
                codename=f"view_{codename}", content_type=ct
            ).first()
            if perm:
                observer_perms.append(perm)

    observer.permissions.add(*observer_perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["observer", "manager"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("sklad_logic", "0001_initial"),
    ]

    operations = [
        RunPython(create_groups, remove_groups),
    ]