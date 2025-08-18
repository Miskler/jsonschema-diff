Compares – what is?
===================

Internally the diff engine works with *comparators*.  Each comparator derives
from :class:`jsonschema_diff.core.parameter_base.Compare` and knows how to
inspect a particular JSON‑Schema keyword or data type.

Custom comparators can be plugged into the configuration via
``ConfigMaker``'s ``additional_compare_rules`` parameter.  A comparator class
receives the old and new values and yields human readable rows for the report.

