from bookie_app.model import meta
import logging
log = logging.getLogger('bookie_app')

"""Provide methods to call for loading specific types of db data 

and then clearning them
"""

def run_sql(sql_list):
    """Execute the sql commands listed"""
    for query in sql_list:
        meta.Session.execute(query)

def create_bookmarks():
    """Insert sample bookmark data"""
    sql = [
        u"INSERT INTO bookmarks (`id`, `hash`, `url`)\
                VALUES (1, '234988566c9a0a9cf952cec82b143bf9c207ac16' , 'http://google.com');",
        u"INSERT INTO bookmarks (`id`, `hash`, `url`)\
                values (2, '9580476d3390f47eb2afb2630a92639d21bca300', 'http://yahoo.com');",
        u"INSERT INTO bookmarks (`id`, `hash`, `url`)\
                values (3, '08e1f47055381b5b0c9511ddf6012f4be9f71452', 'http://cnn.com');",
    ]

    run_sql(sql)
    meta.Session.commit()

def clear_bookmarks():
    """Clear the above bookmark data"""
    sql = [
        "DELETE FROM bookmarks;",
    ]

    run_sql(sql)
    meta.Session.commit()

def create_tags():
    """Insert sample tag data"""
    sql = [
        u"INSERT INTO tags (`id`, `name`, `count`)\
                VALUES (1, 'pylons' , 0);",
        u"INSERT INTO tags (`id`, `name`, `count`)\
                values (2, 'python', 0);",
        u"INSERT INTO tags (`id`, `name`, `count`)\
                values (3, 'php', 0);",
    ]

    run_sql(sql)
    meta.Session.commit()

def clear_tags():
    """Clear the above tag data"""
    sql = [
        "DELETE FROM tags;",
    ]

    run_sql(sql)
    meta.Session.commit()

def create_bookmarks_tags():
    """Create data tying the bookmarks listed to the tags listed
    
    bookmark
        - google
            - python, php
        - yahoo
            - php, pylons
        - cnn
            - php
    
    """
    sql = [
        "INSERT INTO bookmarks_tags (`bookmark_id`, `tag_id`)"
            "VALUES (1, 2);",
        "INSERT INTO bookmarks_tags (`bookmark_id`, `tag_id`)"
            "VALUES (1, 3);",
        "INSERT INTO bookmarks_tags (`bookmark_id`, `tag_id`)"
            "VALUES (2, 3);",
        "INSERT INTO bookmarks_tags (`bookmark_id`, `tag_id`)"
            "VALUES (2, 1);",
        "INSERT INTO bookmarks_tags (`bookmark_id`, `tag_id`)"
            "VALUES (3, 3);",
    ]

    run_sql(sql)
    meta.Session.commit()

def clear_bookmarks_tags():
    """Clear out the tied data listed above"""
    sql = [
        "DELETE FROM bookmarks_tags;",
    ]

    run_sql(sql)
    meta.Session.commit()
