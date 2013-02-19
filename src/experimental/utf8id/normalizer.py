import re
import unicodedata
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.http import IHTTPRequest
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
import plone.i18n.normalizer

# Note that we do not override IIDNormalizer since that can be used to
# generated ids for other things that might not accept UTF-8 strings.

IGNORE_REGEX = re.compile(plone.i18n.normalizer.IGNORE_REGEX.pattern, re.UNICODE)
NON_WORD_REGEX = re.compile(plone.i18n.normalizer.NON_WORD_REGEX.pattern, re.UNICODE)
MULTIPLE_DASHES_REGEX = re.compile(plone.i18n.normalizer.MULTIPLE_DASHES_REGEX.pattern, re.UNICODE)
EXTRA_DASHES_REGEX = re.compile(plone.i18n.normalizer.EXTRA_DASHES_REGEX.pattern, re.UNICODE)
URL_DANGEROUS_CHARS_REGEX = re.compile(plone.i18n.normalizer.URL_DANGEROUS_CHARS_REGEX.pattern, re.UNICODE)


@implementer(IURLNormalizer)
class Utf8URLNormalizer(plone.i18n.normalizer.URLNormalizer):
    def normalize(self, text, locale=None, max_length=plone.i18n.normalizer.MAX_URL_LENGTH):
        assert isinstance(text, basestring)
        if isinstance(text, str):
            try:
                unicode_text = text.decode('utf-8')
            except UnicodeDecodeError:
                return super(Utf8URLNormalizer, self).normalize(text, locale, max_length)
        else:
            unicode_text = text
        unicode_text = unicodedata.normalize('NFKC', unicode_text)
        unicode_text = unicode_text.strip().lower()
        unicode_text = IGNORE_REGEX.sub('', unicode_text)
        unicode_text = NON_WORD_REGEX.sub('-', unicode_text)
        unicode_text = URL_DANGEROUS_CHARS_REGEX.sub('-', unicode_text)
        unicode_text = EXTRA_DASHES_REGEX.sub('', unicode_text)
        unicode_text = MULTIPLE_DASHES_REGEX.sub('-', unicode_text)
        unicode_text = plone.i18n.normalizer.cropName(unicode_text, maxLength=max_length)
        assert isinstance(unicode_text, unicode)
        return unicode_text.encode('utf-8')


utf8_url_normalizer = Utf8URLNormalizer()


@adapter(IHTTPRequest)
@implementer(IUserPreferredURLNormalizer)
class Utf8UserPreferredURLNormalizer(object):
    def __init__(self, context):
        self.context = context

    def normalize(self, text):
        return utf8_url_normalizer.normalize(text)
