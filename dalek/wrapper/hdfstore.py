import os
import time
import errno
import logging

from pandas import HDFStore

logger = logging.getLogger(__name__)


class SafeHDFStore(HDFStore):
    def __init__(self, *args, **kwargs):
        probe_interval = kwargs.pop("probe_interval", 1)
        self._lock = "%s.lock" % args[0]
        while True:
            try:
                self._flock = os.open(self._lock, os.O_CREAT |
                                                  os.O_EXCL |
                                                  os.O_WRONLY)
                break
            except OSError as e:
                if e.errno == errno.EEXIST:
                    time.sleep(probe_interval)
                else:
                    raise e

        HDFStore.__init__(self, *args, **kwargs)

    def __exit__(self, *args, **kwargs):
        logger.debug('Exit SafeHDFStore')
        HDFStore.__exit__(self, *args, **kwargs)
        os.close(self._flock)
        os.remove(self._lock)
