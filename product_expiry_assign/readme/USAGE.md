This module allows to do so by setting a context key to force the reservation of expired lots.

Before calling `<stock.move>._action_confirm()` or `<stock.move>._action_assign()`,
one could set the `ignore_expiration_date` context key:

```python
move_expired_lot._action_assign()
assert move_expired_lot.state == "confirmed"
move_expired_lot.with_context(ignore_expiration_date=True)._action_assign()
assert move_expired_lot.state == "assigned"
```
