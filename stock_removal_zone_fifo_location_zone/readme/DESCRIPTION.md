Glue module between `stock_removal_zone_fifo` and `stock_location_zone`,
installed automatically when both are.

`stock_removal_zone_fifo` takes a zone to be the nearest ancestor location
carrying the Zone-Level FIFO strategy. This module replaces that definition with
the zones of `stock_location_zone`, so the goods keep their zone entry date while
they stay under the same location flagged `Is a Zone Location?`.

Install it when the zones of your warehouse do not line up with the locations you
set the removal strategy on. Moves with no location flagged `Is a Zone Location?`
on either side keep the definition of `stock_removal_zone_fifo`, so installing
this module without flagging any zone changes nothing.
