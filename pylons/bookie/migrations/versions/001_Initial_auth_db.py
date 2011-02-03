from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' passed in
    meta = MetaData(migrate_engine)

    group_permission_table = Table('group_permission', meta,
        Column('group_id', Integer),
        Column('permission_id', Integer)
    )

    # This is the association table for the many-to-many relationship between
    # groups and members - this is, the memberships.
    user_group_table = Table('user_group', meta,
        Column('user_id', Integer),
        Column('group_id', Integer)
    )

    group_table = Table('group', meta,
        Column('group_id',Integer, autoincrement=True, primary_key=True),
        Column('group_name', Unicode(16), unique=True),
        Column('group_abbrev', Unicode(5), unique=True)
    )

    user_table = Table('user', meta,
        Column('user_id', Integer, autoincrement=True, primary_key=True),
        Column('user_name', Unicode(255), unique=True),
        Column('email', Unicode(255)),
        Column('password', Unicode(80)),
        Column('is_ldap', Boolean(), default=0)
    )

    permission_table = Table('permission', meta,
        Column('permission_id', Integer, autoincrement=True, primary_key=True),
        Column('permission_name', Unicode(16), unique=True)
    )

    group_permission_table.create()
    user_group_table.create()
    group_table.create()
    user_table.create()
    permission_table.create()

    # default passwords are just 'testing'
    sql = [
        "INSERT INTO user (user_id, user_name, email, password, is_ldap) VALUES (1, 'rharding@mitechie.com', 'rharding@mitechie.com','d9b152f3bad2cb0104e560dff48da0c7fe35d9187ea581575c2b4fd185093c1c73b784824c0a1dd1', 0);",
        "INSERT INTO user (user_id, user_name, email, password, is_ldap) VALUES (2, 'testdummy@gmail.com', 'testdummy@gmail.com','d9b152f3bad2cb0104e560dff48da0c7fe35d9187ea581575c2b4fd185093c1c73b784824c0a1dd1', 0);",
        "INSERT INTO user (user_id, user_name, email, password, is_ldap) VALUES (3, 'rharding@morpace.com', 'rharding@morpace.com', NULL, 1);",
        "INSERT INTO `group` (group_id, group_name) VALUES (1, 'admin');",
        "INSERT INTO `group` (group_id, group_name) VALUES (2, 'dp');",
        "INSERT INTO permission (permission_id, permission_name) VALUES (1, 'add_job');",
        "INSERT INTO permission (permission_id, permission_name) VALUES (2, 'pause_domain');",
        "INSERT INTO user_group (user_id, group_id) VALUES (1, 1);",
        "INSERT INTO user_group (user_id, group_id) VALUES (2, 2);",
        "INSERT INTO user_group (user_id, group_id) VALUES (3, 1);",
        "INSERT INTO group_permission (group_id, permission_id) VALUES (1, 1);",
        "INSERT INTO group_permission (group_id, permission_id) VALUES (1, 2);",
        "INSERT INTO group_permission (group_id, permission_id) VALUES (2, 1);",
    ]

    for query in sql:
        migrate_engine.execute(query)

    sql = "INSERT INTO `group` (group_id, group_name) VALUES (3, 'viewer');"
    migrate_engine.execute(sql)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(migrate_engine)

    sql = "DELETE FROM `group` WHERE group_id = 3;"
    migrate_engine.execute(sql)

    group_permission_table = Table('group_permission', meta)
    user_group_table = Table('user_group', meta)
    group_table = Table('group', meta)
    user_table = Table('user', meta)
    permission_table = Table('permission', meta)

    sql = [
        "DELETE FROM user;",
        "DELETE FROM `group`;",
        "DELETE FROM permission;",
        "DELETE FROM user_group;",
        "DELETE FROM group_permission;",
    ]

    for query in sql:
        migrate_engine.execute(query)


    group_permission_table.drop()
    user_group_table.drop()
    group_table.drop()
    user_table.drop()
    permission_table.drop()
