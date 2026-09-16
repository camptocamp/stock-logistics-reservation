A zone is the nearest ancestor location, itself included, whose removal strategy
is zone-based. `stock.location._get_zone_location()` resolves it, and
`_zone_removal_strategies()` lists the strategy methods that define one — a
module adding another zone-based strategy extends that list.

An extension module defining the zones differently overrides one hook on
`stock.move.line` and delegates the decision back:

```python
def _is_zone_changed(self, location):
    return location._compare_zones(<source zone>, <destination zone>)
```

`stock.location._compare_zones` answers `False` when both zones are the same, so the goods keep
their date, and `True` when they enter another zone, so the date is reset. A
destination in no zone answers `False` too, unless the company setting
`zone_in_date_reset_out_of_zone` is on.

When the destination location already holds stock, the returned date competes
with the one already stored and the oldest of the two wins, so arriving goods
never push the ones already there back in the queue. This mirrors the way the
core keeps the oldest `in_date` when it merges stock into an existing quant.
