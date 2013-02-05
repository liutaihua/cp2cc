from datetime import time, datetime

from pytz.reference import FixedOffset

from mochiads_lib.util import PST8PST8


def _make_tz_tuple(offset):
    if offset == 0:
        t = FixedOffset(0, "UTC")
    else:
        sign = "+"

        if offset < 0:
            sign = "-"

        t = FixedOffset(offset*60, "UTC%s%s" % (sign, abs(offset)))

    return (t.tzname(None), t)


_timezones = dict([_make_tz_tuple(o) for o in xrange(-12, 13)])


utc_timezones = [x for x,y in sorted(_timezones.iteritems(),
                                     key=lambda z: z[1].utcoffset(None))]


_other_areas = {
    'UTC-10': ['US/Hawaii'],
    'UTC-8': ['US/Pacific'],
    'UTC-7': ['US/Mountain'],
    'UTC-6': ['US/Central'],
    'UTC-5': ['US/Eastern'],
    'UTC': ['Europe/London'],
    'UTC+1': ['Europe/Stockholm', 'Europe/Berlin', 'Europe/Amsterdam',
              'Europe/Madrid', 'Europe/Paris'],
    'UTC+2': ['Europe/Helsinki'],
    'UTC+3': ['Europe/Moscow'],
    'UTC+8': ['Asia/Kuala_Lumpur', 'Asia/Taipei'],
    'UTC+10': ['Australia/Sydney'],
}


_areas_to_zones = {}

for zone, areas in _other_areas.iteritems():
    for area in areas:
        _areas_to_zones[area] = zone


def make_common(zones, other_areas):
    common_zones = []

    for t in zones:
        common_zones.append(t)

        if t in other_areas:
            common_zones.extend(sorted(other_areas[t]))

    return common_zones


common_timezones = make_common(utc_timezones, _other_areas)


def timezone(name):
    if name in _areas_to_zones:
        name = _areas_to_zones[name]

    return _timezones[name.upper()]


def campaign_date_for_db(date, in_timezone, starting=True):
    hour = 0
    if not starting:
        hour = 23

    # Get the time in the given timezone with hour 0 if this is a start date
    # and 23 if this an end date.
    time_w_hour = time(hour=hour)

    # Combine the date to the time
    date_in_tz = datetime.combine(date, time_w_hour)

    # Set the TZinfo object
    loc_date = date_in_tz.replace(tzinfo=timezone(in_timezone))

    # Convert the datetime to PST8PST8 because that is what the DB uses.
    date_in_pst = loc_date.astimezone(PST8PST8)

    # Truncate the date by making sure minute and second are 0
    trunc_date_in_pst = date_in_pst.replace(minute=0, second=0)

    # Return the correct datetime in the given timezone as truncated PST8PST8
    return trunc_date_in_pst


def campaign_date_for_display(dt, in_timezone):
    tz = timezone(in_timezone)
    dt_at_offset_of_tz = dt.astimezone(tz)
    return dt_at_offset_of_tz
