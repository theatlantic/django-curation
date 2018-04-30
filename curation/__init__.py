import django
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('django-curation').version
except pkg_resources.DistributionNotFound:
    __version__ = None

IS_DJANGO_GTE_1_11 = (django.VERSION >= (1, 11))
