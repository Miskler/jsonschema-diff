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


Comparator-specific settings (advanced)
---------------------------------------

Use ``Config.COMPARE_CONFIG`` for comparator-specific knobs.
For such cases, configure :class:`~jsonschema_diff.core.config.Config` directly.

For :py:class:`~jsonschema_diff.core.custom_compare.list.CompareList`:

* ``DICT_MATCH_THRESHOLD`` (``float``, default: ``0.10``) controls how strictly
  dictionary elements are matched inside arrays.
* This is intentionally **not** exposed as a dedicated ``ConfigMaker`` argument.

.. code-block:: python

   from jsonschema_diff.core import Config
   from jsonschema_diff.core.custom_compare import CompareList

   config = Config(
       compare_rules={
           list: CompareList,
       },
       compare_config={
           CompareList: {
               "DICT_MATCH_THRESHOLD": 0.25,
           },
       },
   )
