from playhouse.migrate import *
from peewee import *

database = SqliteDatabase('database.db')
migrator = SqliteMigrator(database)

# Применение миграции
def apply_migration(migration_name):
    if migration_name == '001_change_url_field_type':
        migrate(
            migrator.alter_column_type('button', 'url', TextField(null=True))
        )
    else:
        print(f"Миграции с именем '{migration_name}' не существует.")


if __name__ == '__main__':
    import sys
    try:
        migration_name = sys.argv[1]
    except IndexError:
        print("Укажите название миграции для применения.")
        sys.exit(1)

    apply_migration(migration_name)