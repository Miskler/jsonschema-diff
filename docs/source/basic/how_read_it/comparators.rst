Custom comparators
==================

A comparator is a handler for properties.
It defines how exactly properties will be compared and displayed.
It also defines the legend for them.

Base Compare
------------

.. jsonschemadiff:: basic/how_read_it/jsons/base.old.schema.json  basic/how_read_it/jsons/base.new.schema.json
   :title: Terminal


List / Array Compare
--------------------

.. jsonschemadiff:: basic/how_read_it/jsons/array.old.schema.json basic/how_read_it/jsons/array.new.schema.json
   :title: Terminal


To disable it use:

.. code-block:: python

    ConfigMaker.make(list_comparator = False)


Range Compare
-------------

.. jsonschemadiff:: basic/how_read_it/jsons/range.old.schema.json basic/how_read_it/jsons/range.new.schema.json
   :title: Terminal


To disable it use:

.. code-block:: python

    ConfigMaker.make(
        range_digit_comparator = False,
        range_length_comparator = False,
        range_items_comparator = False,
        range_properties_comparator = False,
    )

Real-world example
------------------

.. jsonschemadiff:: basic/how_read_it/jsons/realworld.old.schema.json basic/how_read_it/jsons/realworld.new.schema.json
   :title: Terminal
