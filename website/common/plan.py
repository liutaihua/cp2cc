import datetime
from functools import partial

class Plan(object):
    def __init__(self, func):
        assert callable(func)
        self.func = func

    def print_exec_body(self):
        if isinstance(self.func, partial):
            args_in_str = map(str, self.func.args)
            print '%s(%s)' % (self.func.func.__name__, ', '.join(args_in_str))
        elif hasattr(self.func, '__name__'):
            print '%s()' % self.func.__name__
        else:
            print 'Execute %s.' % str(self.func)

    def execute(self):
        self.func()

class FixedTimePlan(Plan):
    def __init__(self, func, **kwargs):
        """
        datetime.time(hour[, minute[, second[, microsecond[, tzinfo]]]])
        """
        super(FixedTimePlan, self).__init__(func)
        self.time = datetime.time(**kwargs)

    def next_datetime(self):
        now = datetime.datetime.now()
        if self.time > now.time():
            return datetime.datetime.combine(now.date(), self.time)
        else:
            tomorrow = now + datetime.timedelta(days=1)
            return datetime.datetime.combine(tomorrow.date(), self.time)

class FixedIntervalPlan(Plan):
    def __init__(self, func, **kwargs):
        """
        datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
        """
        super(FixedIntervalPlan, self).__init__(func)
        self.interval = datetime.timedelta(**kwargs)

    def next_datetime(self):
        return datetime.datetime.now() + self.interval
