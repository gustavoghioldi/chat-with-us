import logging
from django.db import models
from six import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _

LOG_LEVELS = (
    (logging.NOTSET, _('NotSet')),
    (logging.INFO, _('Info')),
    (logging.WARNING, _('Warning')),
    (logging.DEBUG, _('Debug')),
    (logging.ERROR, _('Error')),
    (logging.FATAL, _('Fatal')),
)


@python_2_unicode_compatible
class StatusLog(models.Model):
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.ERROR, db_index=True)
    logger = models.CharField(max_length=100)
    message = models.TextField()
    pathname = models.CharField(max_length=100)
    funcname = models.CharField(max_length=100)
    lineno = models.IntegerField()
    trace = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at', db_index=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = verbose_name = 'Logging'