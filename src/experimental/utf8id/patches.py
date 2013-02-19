import cgi
import logging
import re
from Acquisition import aq_base
from zExceptions import BadRequest
from OFS.ObjectManager import NOT_REPLACEABLE
from OFS.ObjectManager import REPLACEABLE
from OFS.ObjectManager import UNIQUE
# Modules to patch
import OFS.ObjectManager
import Products.CMFCore.DirectoryView
import Products.CMFFormController
import Products.CMFPlone.PloneTool


log = logging.getLogger(__name__)

CONTAINS_EVIL = re.compile(r'[^\w~,.$\(\)# @-]', re.UNICODE)


def bad_id(id):
    """Perform a basic check for invalid ids.

    The original version is a bound search method for a regular expression, which
    explains the strange API: None must be returned for a valid id success and
    any other value for illegal ids. This version does a little bit of extra
    work to check for valid UTF-8 encoding and allow all unicode alphanumerics.
    """
    assert isinstance(id, str)
    try:
        unicode_id = id.decode('utf-8')
    except UnicodeDecodeError:
        return 'Invalid UTF-8 encoding'
    return CONTAINS_EVIL.search(unicode_id)


def checkValidId(self, id, allow_dup=False):
    if not id or not isinstance(id, str):
        if isinstance(id, unicode):
            id = cgi.escape(id)
        raise BadRequest('Empty or invalid id specified: %s' % id)

    safe_id = cgi.escape(id)

    try:
        unicode_id = id.decode('utf-8')
    except UnicodeDecodeError:
        raise BadRequest('The id "%s" is not a valid UTF-8 string.' % safe_id)

    if CONTAINS_EVIL.search(unicode_id) is not None:
        raise BadRequest('The id "%s" contains characters illegal in URLs.' % safe_id)
    if id in {'.', '..'}:
        raise BadRequest('The id "%s" is invalid because it is not traversable.' % safe_id)
    if id.startswith('_'):
        raise BadRequest('The id "%s" is invalid because it begins with an underscore.' % safe_id)
    if id.startswith('aq_'):
        raise BadRequest('The id "%s" is invalid because it begins with "aq_".' % safe_id)
    if id.endswith('__'):
        raise BadRequest('The id "%s" is invalid because it ends with two underscores.' % safe_id)
    if not allow_dup:
        obj = getattr(self, id, None)
        if obj is not None:
            # An object by the given id exists either in this
            # ObjectManager or in the acquisition path.
            flags = getattr(obj, '__replaceable__', NOT_REPLACEABLE)
            if hasattr(aq_base(self), id):
                # The object is located in this ObjectManager.
                if not flags & REPLACEABLE:
                    raise BadRequest('The id "%s" is invalid - it is already in use.' % safe_id)
                # else the object is replaceable even if the UNIQUE
                # flag is set.
            elif flags & UNIQUE:
                raise BadRequest('The id "%s" is reserved.' % safe_id)
    if id == 'REQUEST':
        raise BadRequest('REQUEST is a reserved name.')
    if '/' in id:
        raise BadRequest('The id "%s" contains characters illegal in URLs.' % safe_id)


def bad_chars(self, id):
    if isinstance(id, str):
        try:
            id = id.decode('utf-8')
        except UnicodeDecodeError:
            pass

    return CONTAINS_EVIL.findall(id)


_patches = {}


def _update_globals(original, new):
    new_globals = set(new.func_globals) - set(original.func_globals)
    for key in new_globals:
        original.func_globals[key] = new.func_globals[key]


def patch():
    if 'checkValidId' not in _patches:
        log.info('Replacing checkValidId with custom version.')
        _patches['checkValidId'] = OFS.ObjectManager.checkValidId.func_code
        _update_globals(OFS.ObjectManager.checkValidId, checkValidId)
        OFS.ObjectManager.checkValidId.func_code = checkValidId.func_code
    if 'bad_id' not in _patches:
        log.info('Replacing bad_id with custom version.')
        _patches['bad_id'] = OFS.ObjectManager.bad_id
        OFS.ObjectManager.bad_id = bad_id
        Products.CMFCore.DirectoryView.bad_id = bad_id
        Products.CMFFormController.FormController.bad_id = bad_id
        Products.CMFPlone.PloneTool.bad_id = bad_id
    if 'bad_chars' not in _patches:
        log.info('Replacing PloneTool.bad_chars with custom version.')
        _patches['bad_chars'] = Products.CMFPlone.PloneTool.PloneTool.bad_chars.func_code
        _patches['BAD_CHARS'] = Products.CMFPlone.PloneTool.BAD_CHARS
        del Products.CMFPlone.PloneTool.BAD_CHARS
        _update_globals(Products.CMFPlone.PloneTool.PloneTool.bad_chars.im_func, bad_chars)
        Products.CMFPlone.PloneTool.PloneTool.bad_chars.im_func.func_code = bad_chars.func_code


def unpatch():
    if 'checkValidId' in _patches:
        log.info('Restoring original checkValidId.')
        original = _patches.pop('checkValidId')
        OFS.ObjectManager.checkValidId.func_code = original
    if 'bad_id' in _patches:
        original = _patches.pop('bad_id')
        OFS.ObjectManager.bad_id = original
        Products.CMFCore.DirectoryView.bad_id = original
        Products.CMFFormController.FormController.bad_id = original
        Products.CMFPlone.PloneTool.bad_id = original
    if 'bad_chars' in _patches:
        log.info('Restoring original PloneTool.bad_chars.')
        Products.CMFPlone.PloneTool.PloneTool.bad_chars.im_.func_code = _patches.pop('bad_chars')
        Products.CMFPlone.PloneTool.BAD_CHARS = _patches.pop('BAD_CHARS')
