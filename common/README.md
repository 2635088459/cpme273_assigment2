# Common IDs

This folder holds small shared helpers used by multiple parts of the assignment.

## ids.py

The `ids.py` module provides simple UUID-based ID generators with prefixes:

- `new_order_id()` -> `order-<uuid>`
- `new_reservation_id()` -> `res-<uuid>`
- `new_notification_id()` -> `notif-<uuid>`
- `new_trace_id()` -> `trace-<uuid>`
- `new_message_id()` -> `msg-<uuid>`

Example usage:

```python
from ids import new_order_id

order_id = new_order_id()
```
