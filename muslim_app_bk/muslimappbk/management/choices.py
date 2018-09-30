from django.utils.translation import gettext_lazy as _

APPROVE_CHOICES = (
                   ('new', _('new')),
                   ('approved', _('approved')),
                   ('rejected', _('rejected'))
                   )
ACTIVE_CHOICES = (('active', _('active')), ('inactive', _('inactive')))

GENDER_CHOICES = (('male', _('male')), ('female', _('female')))