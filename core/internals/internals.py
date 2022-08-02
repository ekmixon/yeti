import importlib
import pkgutil

from mongoengine import IntField, StringField

from core.constants import DB_VERSION
from core.constants import MIGRATIONS_DIRECTORY
from core.database import YetiDocument


class Internals(YetiDocument):
    db_version = IntField(default=DB_VERSION)
    name = StringField(default="default", unique=True)
    __internal = None

    @classmethod
    def syncdb(cls):
        current_version = cls.get_internals().db_version
        if DB_VERSION > current_version:
            print(f"[+] Database version outdated: {current_version} vs. {DB_VERSION}")
            cls.apply_migrations(current_version, DB_VERSION)
        else:
            print("[+] Database version is synced with code.")

    @classmethod
    def get_internals(cls):
        if cls.__internal is None:
            cls.__internal = Internals.get_or_create(name="default")
        return cls.__internal

    @classmethod
    def apply_migrations(cls, current_version, target_version):
        print("    Applying migrations...")
        print(f"    Current version: {current_version}")
        print(f"    Syncing to version: {target_version}")
        internal_version = current_version

        migrations = pkgutil.walk_packages([MIGRATIONS_DIRECTORY], prefix=".")

        for _, name, _ in sorted(migrations, key=lambda m: int(m[1].split("_")[-1])):
            migration_version = int(name.split("_")[-1])
            if (
                internal_version < target_version
                and migration_version <= target_version
                and migration_version > internal_version
            ):
                migration = importlib.import_module(
                    name, package="core.internals.migrations"
                )
                description = migration.__description__
                print(
                    f"        * Applying change ({internal_version} -> {migration_version}): {description}"
                )

                migration.migrate()
                cls.__internal.db_version = migration_version
                cls.__internal.save()
                internal_version = migration_version
