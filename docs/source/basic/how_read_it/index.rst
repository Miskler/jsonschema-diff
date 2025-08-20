How read it?
============

Path
----

The library displays paths in a Python-like way.
This means that keys like "properties" and "items" are not displayed.

We take it for granted that each element in the path is an object.
Its properties (type, format, etc...) are displayed with a dot prefix.

The path is displayed the same way as you would write it in Python - ["path"]["to"]["element"].

Arrays are displayed as numbers from 0 to infinity (index shows which element in the array is meant).
For example ["array"][0]["element"].


.. jsonschemadiff:: basic/how_read_it/jsons/path.array.old.schema.json  basic/how_read_it/jsons/path.array.new.schema.json
   :title: Terminal
   :no-legend:


In the path there can be properties, for example `$def` - it is not a part of a real JSON path,
we can't access it in a real JSON, but it exists in the schema. For example `["somepath"].$def["some"]["property"]`.

Prefixes
--------

The following prefixes exist:

* `"+"`  addition
* `"-"`  removal
* `"r"`  replacement
* `"m"`  modification of the content *(differs from replacement in that not the whole element is replaced, but its part)*
* `" "`  no changes
* `"?"`  undefined *(in essence is an error)*

If the prefixes `+` / `-` are defined in the same line as the path, 
this means that the status is global for the object.
That is, not a property, but an object as a whole is added!

Multiline
---------

To minimize the used space, 
if the changes affect 1 parameter of an object, 
or an object with 1 parameter was changed - everything is displayed in one line, 
in other cases, multiline display is used.

Context
-------

Some parameters may trigger the display of other parameters.
They will be displayed as no-diff changes, 
but will give necessary information to understand changed parameters.

For more information see - :ref:`Context rules <context_rules>`.

Combine
-------

Some groups of parameters have custom handlers.
For example the handler :class:`~jsonschema_diff.core.custom_compare.CompareRange` combines the following fields:

* ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum")
* ("minLength", "maxLength")
* ("minItems", "maxItems")
* ("minProperties", "maxProperties")

.. toctree::
   :maxdepth: 4

   comparators
