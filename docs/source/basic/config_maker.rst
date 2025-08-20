Config Maker
============

:class:`~jsonschema_diff.config_maker.ConfigMaker` assembles a :class:`~jsonschema_diff.core.config.Config` with sensible
defaults. Each switch enables a family of comparison rules.

You can use :class:`~jsonschema_diff.core.config.Config` directly if you need more detailed settings.
ConfigMaker only simplifies the process by including standard templates.

For detailed information about the allowed parameters, see :py:meth:`~jsonschema_diff.config_maker.ConfigMaker.make`

.. code-block:: python

   from jsonschema_diff import ConfigMaker

   # Minimal default configuration
   config = ConfigMaker.make()

   # Fine tuned configuration
   config = ConfigMaker.make(
       tab_size=4,
       list_comparator=False,          # disable list diffing
       additional_compare_rules={str: CustomComparator},
   )

The resulting object is :py:class:`~jsonschema_diff.core.config.Config`.

