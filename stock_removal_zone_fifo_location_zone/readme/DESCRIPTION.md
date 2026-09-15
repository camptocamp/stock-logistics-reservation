Glue module between `stock_removal_zone_fifo` and `stock_location_zone`,
installed automatically when both are.

`stock_removal_zone_fifo` resets the `Zone Entry Date` of the goods on every
move, because on its own it has no notion of what a zone is. This module answers
that question with the zones of `stock_location_zone`: the goods keep their zone
entry date as long as the source and the destination locations belong to the
same zone, and only get a fresh one when they really enter another zone.

Without it, an internal reorganisation inside a picking zone would send the
moved goods to the back of the Zone-Level FIFO queue.
