Set `Zone-Level FIFO` as the removal strategy of a location, or of a product
category.

On its own this module has no notion of what a zone is, so every move resets the
zone entry date of the destination quant and the strategy behaves like the
standard FIFO. Install an extension module defining the zones to make it useful,
for instance `stock_removal_zone_fifo_location_zone`.
