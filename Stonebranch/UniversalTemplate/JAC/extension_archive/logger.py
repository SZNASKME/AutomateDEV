import logging
from os import getenv
from typing import Union


# disabling but keeping this filter for future use becuase of a bug in uac
# where long log files get truncated
class ReducedVerbosity(logging.Filter):
    _ignore = ["Response retrieved:  Status code 200", "Executing REST API:"]

    if getenv("JAC_REDUCE_VERBOSITY") is not None:
        _ignore.append("UC Definition")

    def filter(self, record: logging.LogRecord) -> Union[bool, logging.LogRecord]:
        msg = record.getMessage()
        return not any(i in msg for i in self._ignore)


logger = logging.getLogger("UNV")
# logger.addFilter(ReducedVerbosity())
