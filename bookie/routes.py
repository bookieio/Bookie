"""Create routes here and gets returned into __init__ main()"""
from convoy.combo import combo_app
from pyramid.wsgi import wsgiapp2


def build_routes(config):
    """Add any routes to the config"""

    config.add_route("home", "/")
    config.add_route("dashboard", "/dashboard")

    # Add routes for the combo loader to match up to static file requests.
    config.add_route('convoy', '/combo')

    JS_FILES = config.get_settings()['app_root'] + '/bookie/static/js/build'
    application = combo_app(JS_FILES)
    config.add_view(
        wsgiapp2(application),
        route_name='convoy')

    # auth routes
    config.add_route("login", "login")
    config.add_route("logout", "logout")
    config.add_route("reset", "{username}/reset/{reset_key}")
    config.add_route("signup", "signup")
    config.add_route("signup_process", "signup_process")

    # celery routes
    config.add_route("celery_hourly_stats", "jobhourly")

    # bmark routes
    config.add_route("bmark_recent", "recent")
    config.add_route("bmark_recent_tags", "recent/*tags")

    config.add_route("bmark_recent_rss", "rss")
    config.add_route("bmark_recent_rss_tags", "rss/*tags")

    config.add_route("bmark_readable", "bmark/readable/{hash_id}")

    # user based bmark routes
    config.add_route("user_bmark_recent", "{username}/recent")
    config.add_route("user_bmark_recent_tags", "{username}/recent/*tags")

    config.add_route("user_bmark_rss", "{username}/rss")
    config.add_route("user_bmark_rss_tags", "{username}/rss/*tags")

    config.add_route("user_bmark_edit", "{username}/edit/{hash_id}")
    config.add_route("user_bmark_edit_error",
                     "{username}/edit_error/{hash_id}")
    config.add_route("user_bmark_new", "{username}/new")
    config.add_route("user_bmark_new_error", "{username}/new_error")
    config.add_route(
        "user_delete_all_bookmarks",
        "{username}/account/delete_all_bookmarks")

    # config.add_route("bmark_delete", "/bmark/delete")
    # config.add_route("bmark_confirm_delete", "/bmark/confirm/delete/{bid}")

    # tag related routes
    config.add_route("tag_list", "tags")
    config.add_route("tag_bmarks", "tags/*tags")

    # user tag related
    config.add_route("user_tag_list", "{username}/tags")
    config.add_route("user_tag_bmarks", "{username}/tags/*tags")

    config.add_route("user_import", "{username}/import")
    config.add_route("search", "search")
    config.add_route("user_search", "{username}/search")

    config.add_route("search_results", "results")
    config.add_route("user_search_results", "{username}/results")

    # matches based on the header
    # HTTP_X_REQUESTED_WITH
    # ajax versions are used in the mobile search interface
    config.add_route("search_results_ajax", "results/*terms", xhr=True)
    config.add_route("search_results_rest", "results/*terms")
    config.add_route("user_search_results_ajax",
                     "{username}/results*terms",
                     xhr=True)
    config.add_route("user_search_results_rest", "{username}/results*terms")

    config.add_route("redirect", "redirect/{hash_id}")
    config.add_route("user_redirect", "{username}/redirect/{hash_id}")

    config.add_route("user_account", "{username}/account")
    config.add_route("user_export", "{username}/export")
    config.add_route("user_stats", "{username}/stats")

    # oauth urls
    config.add_route("twitter_connect", "oauth/twitter_connect")

    #
    # NEW API
    #

    # stats
    config.add_route('api_bookmark_stats',
                     '/api/v1/stats/bookmarks',
                     request_method='GET')
    config.add_route('api_user_stats',
                     '/api/v1/stats/users',
                     request_method='GET')

    # ping checks
    config.add_route('api_ping',
                     '/api/v1/{username}/ping',
                     request_method='GET')
    config.add_route('api_ping_missing_user',
                     '/api/v1/ping',
                     request_method='GET')
    config.add_route('api_ping_missing_api',
                     '/ping',
                     request_method='GET')

    # auth related
    config.add_route("api_user_account",
                     "/api/v1/{username}/account",
                     request_method="GET")
    config.add_route("api_user_account_update",
                     "/api/v1/{username}/account",
                     request_method="POST")
    config.add_route("api_user_api_key",
                     "/api/v1/{username}/api_key",
                     request_method="GET")
    config.add_route("api_reset_api_key",
                     "/api/v1/{username}/api_key",
                     request_method="POST")
    config.add_route("api_user_reset_password",
                     "/api/v1/{username}/password",
                     request_method="POST")

    config.add_route("api_user_suspend_remove",
                     "api/v1/suspend",
                     request_method="DELETE")
    config.add_route("api_user_suspend",
                     "api/v1/suspend",
                     request_method="POST")
    config.add_route("api_user_invite",
                     "api/v1/{username}/invite",
                     request_method="POST")

    # many bookmark api calls
    config.add_route("api_bmarks_export", "api/v1/{username}/bmarks/export")

    # we have to search before we hit the bmarks keys so that it doesn't think
    # the tag is "search"
    config.add_route("api_bmark_search", "api/v1/bmarks/search/*terms")
    config.add_route("api_bmark_search_user",
                     "/api/v1/{username}/bmarks/search/*terms")

    config.add_route('api_bmarks', 'api/v1/bmarks')
    config.add_route('api_bmarks_tags', 'api/v1/bmarks/*tags')
    config.add_route('api_bmarks_user', 'api/v1/{username}/bmarks')
    config.add_route('api_bmarks_user_tags', 'api/v1/{username}/bmarks/*tags')
    config.add_route('api_count_bmarks_user',
                     'api/v1/{username}/stats/bmarkcount')

    # user bookmark api calls
    config.add_route("api_bmark_add",
                     "/api/v1/{username}/bmark",
                     request_method="POST")
    config.add_route("api_bmark_update",
                     "/api/v1/{username}/bmark/{hash_id}",
                     request_method="POST")
    config.add_route("api_extension_sync", "/api/v1/{username}/extension/sync")

    config.add_route("api_bmark_hash",
                     "/api/v1/{username}/bmark/{hash_id}",
                     request_method="GET")
    config.add_route("api_bmark_remove",
                     "/api/v1/{username}/bmark/{hash_id}",
                     request_method="DELETE")

    config.add_route("api_tag_complete_user",
                     "/api/v1/{username}/tags/complete")
    config.add_route("api_tag_complete",
                     "/api/v1/tags/complete")

    config.add_route("api_social_connections",
                     "/api/v1/{username}/social_connections")

    # admin api calls
    config.add_route("api_admin_readable_todo", "/api/v1/a/readable/todo")
    config.add_route(
        "api_admin_readable_reindex",
        "/api/v1/a/readable/reindex")
    config.add_route(
        "api_admin_accounts_inactive",
        "/api/v1/a/accounts/inactive")
    config.add_route(
        "api_admin_accounts_invites_add",
        "/api/v1/a/accounts/invites/{username}/{count}",
        request_method="POST")
    config.add_route(
        "api_admin_accounts_invites",
        "/api/v1/a/accounts/invites",
        request_method="GET")
    config.add_route(
        "api_admin_imports_list",
        "/api/v1/a/imports/list",
        request_method="GET")
    config.add_route(
        "api_admin_imports_reset",
        "/api/v1/a/imports/reset/{id}",
        request_method="POST")
    config.add_route(
        "api_admin_twitter_refresh_all",
        "/api/v1/a/social/twitter_refresh/all",
        request_method="GET")
    config.add_route(
        "api_admin_twitter_refresh",
        "/api/v1/a/social/twitter_refresh/{username}",
        request_method="GET")

    config.add_route(
        "api_admin_users_list",
        "/api/v1/a/users/list",
        request_method="GET")
    config.add_route(
        "api_admin_new_user",
        "/api/v1/a/users/add",
        request_method="POST")
    config.add_route(
        "api_admin_del_user",
        "/api/v1/a/users/delete/{username}",
        request_method="DELETE")
    config.add_route(
        "api_admin_bmark_remove",
        "/api/v1/a/bmark/{username}/{hash_id}",
        request_method="DELETE")

    config.add_route(
        "api_admin_applog",
        "/api/v1/a/applog/list",
        request_method="GET")

    config.add_route(
        "api_admin_non_activated",
        "/api/v1/a/nonactivated",
        request_method="GET")

    config.add_route(
        "api_admin_delete_non_activated",
        "/api/v1/a/nonactivated",
        request_method="DELETE")

    # these are single word matching, they must be after /recent /popular etc
    config.add_route("user_home", "{username}")

    return config
