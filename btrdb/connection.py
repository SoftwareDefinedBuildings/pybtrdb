from collections import namedtuple
import sqlalchemy
import isodate
import datetime
import math
import requests
def date(dst):
    """
    This parses a modified isodate into nanoseconds since the epoch. The date format is:
    YYYY-MM-DDTHH:MM:SS.NNNNNNNNN
    Fields may be omitted right to left, but do not elide leading or trailing zeroes in any field
    """
    idate = dst[:26]
    secs = (isodate.parse_datetime(idate) - datetime.datetime(1970,1,1)).total_seconds()
    nsecs = int(secs*1000000) * 1000
    nanoS = dst[26:]
    if len(nanoS) != 3 and len(nanoS) != 0:
        raise Exception("Invalid date string!")
    if len(nanoS) == 3:
        nsecs += int(nanoS)
    return nsecs

Point = namedtuple("Point",["time","min","mean","max","count"])

class UUIDResolver(object):
    def __init__(self, server, username, password, database, port=3306):
        """
        Initialises a connection to a MySQL database for
        resolving paths to UUIDs. Note that a UUID resolver only
        lasts a little bit before the connection times out
        """
        self.server = server
        self.port = port
        constring = "mysql://{}:{}@{}:{}/{}".format(
            username, password, server, port, database)
        print constring
        eng = sqlalchemy.create_engine("mysql://uuidresolver:simplepass@miranda.cs.berkeley.edu:3306/upmu")
        print dir(eng)
        print eng.engine
        print eng.connect
        print eng.raw_connection
        print eng.url
        self.conn = eng.connect()

    def resolve(self, path):
        res = self.conn.execute("select path, uuid from uuidpathmap where path like '%%%%%s%%%%'" % path)
        rvs = [(r["uuid"], r["path"]) for r in res]
        if len (rvs) > 1:
            print "Got multiple results for path:"
            for r in rvs:
                print r
            print "returning uuid for ", rvs[0][1]
        return rvs[0][0]

class HTTPConnection(object):
    MAX_RAW = 150000
    def __init__(self, server, port=9000):
        """
        Initialises a connection to a BTrDB server over HTTP
        """
        self.server = server
        self.port = port

    def est_stat_count(self, start, end, pw):
        """
        Estimate the number of statistical records that will be
        returned for the given point width between the two times. This is
        an upper bound, the actual number for a query could be lower than
        this number
        """
        return (end-start) / (1<<pw)

    def est_raw_count(self, uuid, start, end):
        """
        Estimate the number of raw points exist between two times.
        The estimation is an upper bound -- the real number is guaranteed
        to be less than or equal to this nubmer
        """
        wwidth = (end-start) / 16
        pw = int(math.log(wwidth, 2))
        rstart = start & ((1<<pw)-1)
        rend = end & ((1<<pw)-1)
        rend += 1<<pw
        r = requests.get("http://{}:{}/data/uuid/{}?starttime={}&endtime={}&pw={}&unitoftime=ns"
            .format(self.server, self.port, uuid, rstart, rend, pw))
        if r.status_code != 200:
            raise Exception("Quasar didn't like request:"+r.text)
        return sum(x[5] for x in r.json()[0]["XReadings"])

    def get_raw(self, uuid, start, end):
        """
        Request the raw points between the given start time and end time, measured
        in nanoseconds. An estimation of the number of points that will be done is
        performed in advance, and the query is aborted if this exceeds 150K
        """
        if est_raw_count(uuid, start, end) > self.MAX_RAW:
            raise Exception("Raw query is too large")
        raise Exception("This feature not implemented yet")

    def get_stat(self, uuid, start, end, pw=None):
        """
        Get a statistical representation of the data between the given two
        points. If the point width is omitted, it will be automatically
        calculated so as to return approx 1024 records.
        """
        if pw is None:
            pw = int(math.log(end-start,2)) - 10
        else:
            if self.est_stat_count(start, end) > 2048:
                raise Exception("This statistical query is too big")

        r = requests.get("http://{}:{}/data/uuid/{}?starttime={}&endtime={}&pw={}&unitoftime=ns"
            .format(self.server, self.port, uuid, start, end, pw))
        if r.status_code != 200:
            raise Exception("Quasar didn't like request:"+r.text)
        return [ Point (x[0]*1000000 + x[1], x[2], x[3], x[4], x[5]) for x in r.json()[0]["XReadings"] ]
