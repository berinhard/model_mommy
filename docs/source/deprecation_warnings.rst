Deprecation Warnings
====================

Because of the changes of model_mommy's API, the following methods are deprecated and will be removed in one of the future releases:

  * `mommy.make_one` -> should use the method `mommy.make` instead
  * `mommy.prepare_one` -> should use the method `mommy.prepare` instead
  * `mommy.make_many` -> should use the method `mommy.make` with the `_quantity` parameter instead
  * `mommy.make_many_from_recipe` -> should use the method `mommy.make_recipe` with the `_quantity` parameter instead
