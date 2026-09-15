The standard FIFO removal strategy sorts the quants by incoming date
(`in_date`). That date is set when the goods are received and follows them from
location to location, so it cannot tell when they arrived in the zone they are
stored in: a pallet received long ago and only now brought down to a picking
area keeps its old incoming date, and the picker is sent to it before the stock
that has been sitting in that area for weeks.

This module adds a **Zone-Level FIFO** removal strategy. It keeps the FIFO
principle but sorts on a new `Zone Entry Date` (`zone_in_date`) field on the
quant, falling back on the incoming date:

    zone_in_date ASC, in_date ASC, id

`zone_in_date` is set when the goods are put down in a location and, unlike
`in_date`, it is never reset afterwards by a merge of stock or by an inventory
adjustment. It is always set, so the sort above needs no NULL handling.
