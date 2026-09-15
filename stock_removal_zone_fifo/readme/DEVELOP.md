An extension module teaches this one where the zones are by overriding a single
hook on `stock.move.line`:

```python
def _zone_in_date_to_propagate(self, location):
    """Zone entry date the goods get in ``location``, or False."""
    if <location is in the same zone as self.location_id>:
        # the goods were already in it, keep their date
        return self._source_zone_in_date()
    if <location is in a zone>:
        # the goods arrive in it now
        return fields.Datetime.now()
    return super()._zone_in_date_to_propagate(location)
```

`_source_zone_in_date()` reads the date from the quant the goods were taken
from. Returning `False`, the default, changes nothing: the destination quant
keeps the date the core gave it, which is the incoming date carried over from
the source. That is why the strategy behaves like the standard FIFO as long as
no extension module is installed.

When the destination location already holds stock, the returned date competes
with the one already stored and the oldest of the two wins, so arriving goods
never push the ones already there back in the queue. This mirrors the way the
core keeps the oldest `in_date` when it merges stock into an existing quant.
