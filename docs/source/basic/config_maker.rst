Config Maker
============

``ConfigMaker`` assembles a :class:`jsonschema_diff.core.config.Config` with sensible
defaults. Each switch enables a family of comparison rules.

Вы можете использовать напрямую Config если нужны более детальные настройки.
ConfigMaker лишь упрощает процесс включая в себя стандартные шаблоны.

Для детальной информации о допустимых параметрах смотрите :py:meth:`~jsonschema_diff.config_maker.ConfigMaker.make`

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

The resulting object is :py:class:`jsonschema_diff.core.config.Config`.

