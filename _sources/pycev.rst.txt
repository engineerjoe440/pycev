API Reference
=============

The main class for the `pycev` package is `Cev` (also aliased to `CEV`).
This class can be used to interpret SEL CEV files, and provides access
to the various informational data-points for the event record.

.. autoclass:: pycev.Cev
   :members:


Additional Package Functions
----------------------------

.. autofunction:: pycev.row_wise_checksum

.. autofunction:: pycev.split_event_and_relay_data
