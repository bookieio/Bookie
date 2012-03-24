"""Basic views with no home"""
import json
import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from pyramid.view import view_config
from bookie.models.stats import StatBookmarkMgr
from bookie.models.stats import IMPORTER_CT
from bookie.models.stats import TAG_CT
from bookie.models.stats import TOTAL_CT
from bookie.models.stats import UNIQUE_CT


LOG = logging.getLogger(__name__)


@view_config(
    route_name="dashboard",
    renderer="/stats/dashboard.mako")
def dashboard(request):
    """A public dashboard of the system

    To start out, let's dump out some JSON to the body based on:
        - Last 7 days bookmark counts
        - Last 7 days unique bookmark counts
        - Last 7 days tag counts

        - Import queue depth last 7 days
    """
    end = datetime.now()
    start = end - timedelta(days=7)
    check_stats = StatBookmarkMgr.get_stat(start, end,
        TAG_CT, TOTAL_CT, UNIQUE_CT)


    stats_summary = defaultdict(dict)

    for stat in check_stats:
        dt = stat.tstamp.strftime('%m%d %H:%M')
        attrib = stat.attrib
        val = stat.data
        stats_summary[dt][attrib] = val

    unsorted_stats = {}
    for date, data in stats_summary.iteritems():
        data.update({'date': date})
        unsorted_stats[date] = (data)

    dates = unsorted_stats.keys()
    dates.sort()

    final_stats = []
    for d in dates:
        final_stats.push(unsorted_stats[d])

    # check the queue depth over the last while
    start = end - timedelta(hours=12)
    check_stats = StatBookmarkMgr.get_stat(start, end, IMPORTER_CT)
    queue_summary = [
        [],
        []
    ]
    for stat in check_stats:
        dt = stat.tstamp.strftime('%H:%M')
        val = stat.data
        queue_summary[0].append(dt)
        queue_summary[1].append(val)

    stats = {
         'count_summary': json.dumps(final_stats),
         'queue_summary': json.dumps(queue_summary),
    }
    return stats


