"""
Test for quality of results
"""

import music_this_week_app.backend.eventFinder as eventFinder
from datetime import datetime as dt
from datetime import timedelta
from collections import Counter


def in_range(date, start, end):
    return start <= date <= end

def checkDatesInRange():
    """TEST HOW MANY EVENTS ARE IN THE SPECIFIED TIME RANGE"""

    searchArgs = {'location': 'San+Francisco',
                  'date': 'Next+7+Days',
                  'nResults': '300'}
    ef = eventFinder.EventFinder()
    ef.searchForEvents(searchArgs)

    over = 0
    under = 0
    for e in ef.upcomingEvents:
        if in_range(e.date, dt.now()-timedelta(days=0.5), dt.now()+timedelta(days=7)):
            under += 1
        else:
            over += 1
    percent = float(over) / (under + over) * 100

    print "over: %i" % over
    print "under: %i" % under
    print "percent out of bounds: %i" % percent


if __name__ == '__main__':
    checkDatesInRange()