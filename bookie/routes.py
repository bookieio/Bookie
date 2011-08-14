"""Create routes here and gets returned into __init__ main()"""

def build_routes(config):
    """Add any routes to the config"""

    config.add_route("home", "/")

    # auth routes
    config.add_route("login", "login")
    config.add_route("logout", "logout")
    config.add_route("reset", "{username}/reset/{reset_key}")

    # DELAPI Routes
    # config.add_route("del_post_add", "/{username}/delapi/posts/add")
    # config.add_route("del_post_delete", "/{username}/delapi/posts/delete")
    # config.add_route("del_post_get", "/{username}/delapi/posts/get")
    # config.add_route("del_tag_complete", "/{username}/delapi/tags/complete")

    # bmark routes
    config.add_route("bmark_recent", "recent")
    config.add_route("bmark_recent_tags", "recent/*tags")

    config.add_route("bmark_popular", "popular")
    config.add_route("bmark_popular_tags", "popular/*tags")
    config.add_route("bmark_readable", "bmark/readable/{hash_id}")

    # user based bmark routes
    config.add_route("user_bmark_recent", "{username}/recent")
    config.add_route("user_bmark_recent_tags", "{username}/recent/*tags")

    config.add_route("user_bmark_popular", "{username}/popular")
    config.add_route("user_bmark_popular_tags", "{username}/popular/*tags")

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
    config.add_route("search_results_ajax", "results*terms", xhr=True)
    config.add_route("search_results_rest", "results*terms")
    config.add_route("user_search_results_ajax",
                     "{username}/results*terms",
                     xhr=True)
    config.add_route("user_search_results_rest", "{username}/results*terms")


    config.add_route("redirect", "redirect/{hash_id}")
    config.add_route("user_redirect", "{username}/redirect/{hash_id}")

    config.add_route("user_account", "{username}/account")

    # MOBILE routes
    config.add_route("user_mobile", "{username}/m")

    #
    # NEW API
    #

    # auth related
    config.add_route("api_user_account",
                     "/api/v1/{username}/account",
                     request_method="GET")
    config.add_route("api_user_account_update",
                     "/api/v1/{username}/account",
                     request_method="POST")
    config.add_route("api_user_api_key",
                     "/api/v1/{username}/api_key")
    config.add_route("api_user_reset_password",
                     "/api/v1/{username}/password",
                     request_method="POST")
    config.add_route("api_user_suspend_remove",
                     "api/v1/{username}/suspend",
                     request_method="DELETE")
    config.add_route("api_user_suspend",
                     "api/v1/{username}/suspend",
                     request_method="POST")

    # many bookmark api calls
    config.add_route("api_bmarks_export", "api/v1/{username}/bmarks/export")

    config.add_route('api_bmarks', 'api/v1/bmarks')
    config.add_route('api_bmarks_user', 'api/v1/{username}/bmarks')

    config.add_route('api_bmarks_popular', 'api/v1/bmarks/popular')
    config.add_route('api_bmarks_popular_user', 'api/v1/{username}/bmarks/popular')

    config.add_route("api_bmark_search", "api/v1/bmarks/search/*terms")
    config.add_route("api_bmark_search_user",
                     "/api/v1/{username}/bmarks/search/*terms")


    # user bookmark api calls
    config.add_route("api_bmark_add", "/api/v1/{username}/bmark", request_method="POST")
    config.add_route("api_bmark_update", "/api/v1/{username}/bmark/{hash_id}", request_method="POST")
    config.add_route("api_extension_sync", "/api/v1/{username}/extension/sync")

    config.add_route("api_bmark_hash",
                     "/api/v1/{username}/bmark/{hash_id}",
                     request_method="GET")
    config.add_route("api_bmark_remove",
                     "/api/v1/{username}/bmark/{hash_id}",
                     request_method="DELETE")

    config.add_route("api_tag_complete",
                     "/api/v1/{username}/tags/complete")


    # these are single word matching, they must be after /recent /popular etc
    config.add_route("user_home", "{username}")

    return config
