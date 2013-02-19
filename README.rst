This package tries to modify `Zope <http://www.zope.org/>`_ to allow the
use of UTF-8 ids for objects. This makes it possible to use more natural
URLs for non-ASCII content.

How to use
==========

This package can easily be added to your Plone site. You will need to do two
things: install the `experimental.utf8id` package and load its ZCML. If you
are using `zc.buildout <http://www.buildout.org/>`_ this can be done by adding
a few lines to your ``buildout.cfg`` file.

::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    eggs =
        ...
        **experimental.utf8id**
    zcml =
        **experimental.utf8id**
        **experimental.utf8id-overrides**
        ...

After rerunning buildout with the updated configuration your Plone instance
will automatically use UTF-8 ids.

Other requirements are:

* Zope 2.13.20 or later. Currently not yet released.
* plone.portlets 2.2.1 or later. Currently not yet released yet.
* plone.app.portlets 2.4.3 or later (or 2.3.8 or later for the 2.3 branch).
  Currently not yet released.


Why not use unicode ids?
========================

An obvious question is why not allow the use of unicode ids in Zope. If
Zope would be developed today that would be a natural choice. Unfortunately
when Zope was written Python did not support unicode at all, and many parts
of the code base makes assumptions that break if they encounter unicode
instances, leading to `UnicodeDecodeError` exceptions being raised at
unexpected places.


Caveats
=======

Zope has a simple rule: object ids (both the traditional ``id`` attribute and
the newer ``__name__`` attribute **must** be str instances. If any code
violates this rule an object path will contain a mixture of str and unicode
instances which will cause problems if the str instances contain anything other
than stock ASCII characters. Unfortunately means it is not possible to use some
of the newer ZTK code (for example `zope.container
<https://pypi.python.org/pypi/zope.container>`_ base clasess) which use unicode
ids.

If any code imports any of the id checking routines directly it will use
the original implementation. This package will replace such direct imports
with monkey patches for all packages included in a standard Plone install,
but other packages may need to be changes to use module imports. For example
if code currently does this::

   from OFS.ObjectManager import checkValidId
   ...
   if not checkValidId(some_id):
      ...

it can be rewritten like this::

   import OFS.ObjectManager
   ...
   if not OFS.ObjectManager.checkValidId(some_id):
      ...


Implementation details
======================

URL normalization
-----------------

`plone.i18n` implements URL normalization code which is used by Archetypes
to generate ids for new content. This package overrides ``IURLNormalizer``
and ``IUserPreferredURLNormalizer`` to allow all unicode alphanumerical
characters. In order to provide different encodings for the same string
to occur it will normalize the unicode string to NKFC form. 

id checks
---------

There are several utility functions that check if an id is valid. All of these
are replaced using monkey patches with new code paths. The replaces functions
are:

* ``OFS.ObjectManager.checkValidId``
* ``OFS.ObjectManager.ObjectManager._checkId`` (a copy of ``OFS.ObjectManager.checkValidID``)
* ``OFS.ObjectManaged.bad_id``, including places where it is imported directly:
  ``Products.CMFCore.DirectoryView.bad_id``,
  ``Products.CMFFormController.FormController.bad_id`` and
  ``Products.CMFPlone.PloneTool.bad_id``.
* ``Products.CMFPlone.PloneTool.PloneTool.bad_chars``

In addition ``Products.CMFPlone.PloneTool.BAD_CHARS`` is removed to prevent other
code from using it directly.
