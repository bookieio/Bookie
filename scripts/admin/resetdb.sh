#!/bin/zsh


# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_activations" --table "public.activations" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_readable" --table "public.bmark_readable" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_bmark_tags" --table "public.bmark_tags" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_bmarks" --table "public.bmarks" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_import" --table "public.import_queue" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_logging" --table "public.logging" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_stats_bookmarks" --table "public.stats_bookmarks" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_tags" --table "public.tags" "dbname"
# pg_dump --host 127.0.0.1 --port 5432 --format plain --data-only --inserts --column-inserts --verbose --file "bookie_url_hash" --table "public.url_hash" "dbname"

psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_rm_default_user
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_users
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_activations
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_tags
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_logging
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_stats_bookmarks
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_url_hash
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_bmarks
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_bmark_tags
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_readable
psql --host 127.0.0.1 --port 5432 "dbname" -f bookie_import
