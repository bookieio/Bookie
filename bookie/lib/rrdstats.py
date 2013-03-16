"""Handle the creation/updating of the rrd data we want to track"""
import os
import time
from datetime import datetime
from datetime import timedelta

from pyrrd.exceptions import ExternalCommandError
from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF
from pyrrd.graph import LINE
from pyrrd.graph import ColorAttributes, Graph


hour = 60 * 60
day = 24 * hour
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day

today = datetime.now()
delta = timedelta(weeks=28)
start_date = today - delta
step = 3600
maxSteps = 28 * 7 * 24


class SystemCounts(object):
    """Handle the rrd for the system counts"""
    _datafile = 'systemcount.rrd'
    _outputfile = 'systemcount.png'

    @property
    def datafile(self):
        return os.path.join(self.data_root, self._datafile)

    @property
    def outputfile(self):
        return os.path.join(self.output_root, self._outputfile)

    def _boostrap(self):
        """Put together out bits"""
        self.dss = []
        self.ds1 = DS(dsName='bookmark_count', dsType='GAUGE', heartbeat=hour)
        self.ds2 = DS(dsName='unique_count', dsType='GAUGE', heartbeat=hour)
        self.ds3 = DS(dsName='tag_count', dsType='GAUGE', heartbeat=hour)
        self.dss.extend([self.ds1, self.ds2, self.ds3])

        self.rras = []
        rra1 = RRA(cf='AVERAGE', xff=0.5, steps=24, rows=8760)
        self.rras.append(rra1)

        self.myRRD = RRD(
            self.datafile,
            ds=self.dss,
            rra=self.rras,
            start=int(time.mktime(start_date.timetuple())))
        if not os.path.exists(self.datafile):
            # make sure we create the directory
            if not os.path.exists(os.path.dirname(self.datafile)):
                os.makedirs(os.path.dirname(self.datafile))
            self.myRRD.create()

    def __init__(self, data_root, output_root):
        """Bootstrap, does the data file exist, etc"""
        self.data_root = data_root
        self.output_root = output_root
        self._boostrap()

    def output(self, months=3):
        """Render out the image of the rrd"""
        def1 = DEF(
            rrdfile=self.datafile,
            vname='bookmark_count',
            dsName=self.ds1.name)
        def2 = DEF(
            rrdfile=self.datafile,
            vname='unique_count',
            dsName=self.ds2.name)
        def3 = DEF(
            rrdfile=self.datafile,
            vname='tag_count',
            dsName=self.ds3.name)
        line1 = LINE(
            defObj=def1,
            color='#01FF13',
            legend='Bookmarks',
            stack=True)
        line2 = LINE(
            defObj=def2,
            color='#DA7202',
            legend='Unique',
            stack=True)
        line3 = LINE(defObj=def3, color='#BD4902', legend='Tags', stack=True)

        # area1 = AREA(defObj=def1, color='#FFA902', legend='Bookmarks')
        # area2 = AREA(defObj=def2, color='#DA7202', legend='Unique')
        # area3 = AREA(defObj=def3, color='#BD4902', legend='Tags')

        # Let's configure some custom colors for the graph
        ca = ColorAttributes()
        ca.back = '#333333'
        ca.canvas = '#333333'
        ca.shadea = '#000000'
        ca.shadeb = '#111111'
        ca.mgrid = '#CCCCCC'
        ca.axis = '#FFFFFF'
        ca.frame = '#AAAAAA'
        ca.font = '#FFFFFF'
        ca.arrow = '#FFFFFF'

        # Now that we've got everything set up, let's make a graph
        start_date = time.mktime((today - timedelta(weeks=28)).timetuple())
        end_date = time.mktime(today.timetuple())
        g = Graph(self.outputfile,
                  start=int(start_date),
                  end=int(end_date),
                  vertical_label='count',
                  color=ca)
        g.data.extend([def1, def2, def3, line3, line2, line1])

        if not os.path.exists(os.path.dirname(self.outputfile)):
            os.makedirs(os.path.dirname(self.outputfile))

        g.write()

    def mark(self, tstamp, bmarks, uniques, tags):
        """Update the database with some data"""
        timestamp = time.mktime(tstamp.timetuple())
        self.myRRD.bufferValue(int(timestamp), bmarks, uniques, tags)

    def update(self):
        """Update the underlying rrd data"""
        try:
            self.myRRD.update(debug=False)
        except ExternalCommandError, exc:
            print "ERROR", str(exc)


class ImportQueueDepth(object):
    """Handle the rrd for the depth of the import queue"""
    _datafile = 'import_queue_depth.rrd'
    _outputfile = 'import_queue_depth.png'

    @property
    def datafile(self):
        return os.path.join(self.data_root, self._datafile)

    @property
    def outputfile(self):
        return os.path.join(self.output_root, self._outputfile)

    def _boostrap(self):
        """Put together out bits"""
        self.dss = []
        self.ds1 = DS(dsName='depth', dsType='GAUGE', heartbeat=60 * 5)
        self.dss.extend([self.ds1])

        self.rras = []
        rra1 = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=2016)
        self.rras.append(rra1)

        self.myRRD = RRD(
            self.datafile,
            ds=self.dss,
            rra=self.rras,
            start=int(time.mktime(start_date.timetuple())))
        if not os.path.exists(self.datafile):
            # make sure we create the directory
            if not os.path.exists(os.path.dirname(self.datafile)):
                os.makedirs(os.path.dirname(self.datafile))
            self.myRRD.create()

    def __init__(self, data_root, output_root):
        """Bootstrap, does the data file exist, etc"""
        self.data_root = data_root
        self.output_root = output_root
        self._boostrap()

    def output(self, months=3):
        """Render out the image of the rrd"""
        def1 = DEF(
            rrdfile=self.datafile,
            vname='queue',
            dsName=self.ds1.name)
        line1 = LINE(
            defObj=def1,
            color='#01FF13',
            legend='Queue Depth',
            stack=True)
        # area1 = AREA(defObj=def1, color='#FFA902', legend='Bookmarks')

        # Let's configure some custom colors for the graph
        ca = ColorAttributes()
        ca.back = '#333333'
        ca.canvas = '#333333'
        ca.shadea = '#000000'
        ca.shadeb = '#111111'
        ca.mgrid = '#CCCCCC'
        ca.axis = '#FFFFFF'
        ca.frame = '#AAAAAA'
        ca.font = '#FFFFFF'
        ca.arrow = '#FFFFFF'

        # Now that we've got everything set up, let's make a graph
        start_date = time.mktime((today - timedelta(days=7)).timetuple())
        end_date = time.mktime(today.timetuple())
        g = Graph(self.outputfile,
                  start=int(start_date),
                  end=int(end_date),
                  vertical_label='count',
                  color=ca)
        g.data.extend([def1, line1])

        if not os.path.exists(os.path.dirname(self.outputfile)):
            os.makedirs(os.path.dirname(self.outputfile))

        g.write()

    def mark(self, tstamp, depth):
        """Update the database with some data"""
        timestamp = time.mktime(tstamp.timetuple())
        self.myRRD.bufferValue(int(timestamp), depth)

    def update(self):
        """Update the underlying rrd data"""
        try:
            self.myRRD.update(debug=False)
        except ExternalCommandError, exc:
            print "ERROR", str(exc)


if __name__ == "__main__":
    # let's generate some data...
    currentTime = start_date
    value1 = 5100
    value2 = 5000
    value3 = 0000

    rd = SystemCounts('/tmp', '/tmp')

    for i in xrange(maxSteps):
        # lets update the RRD/purge the buffer ever 100 entires
        if i % 10 == 0:
            rd.update()
        # let's do two different sets of periodic values
        value1 = value1 + 1
        value2 = value2 + 1
        value3 = value3 + 1
        currentTime = currentTime + timedelta(seconds=step)
        # when you pass more than one value to update buffer like this,
        # they get applied to the DSs in the order that the DSs were
        # "defined" or added to the RRD object.
        rd.mark(currentTime, value1, value2, value3)
    # add anything remaining in the buffer
    rd.update()
    rd.output()
