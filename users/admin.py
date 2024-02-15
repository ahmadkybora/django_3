import random

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, send_mail
from django.contrib import admin

class UserManager(BaseUserManager):
    user_in_migration = True

    def _create_user(self, username, phone_number, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        if not username:
            raise ValueError('the given username must be set')
        
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number,
                          username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        
        if not extra_fields.get('no_password'):
            user.set_password(password)

        user.save(using=self._db)
        return user
    
    def create_user(self, username=None, phone_number=None, email=None, password=None, **extra_fields):
        if username is None:
            if email:
                username = email.split('@', 1)[0]

            if phone_number:
                username = random.choice('abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]

            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))
        return self._create_user(username, phone_number, email, password, False, False, **extra_fields)
    
    def create_super_user(self, username, phone_number, email, password, **extra_fields):
        return self._create_user(username, phone_number, email, password, True, True, **extra_fields)
    
    def get_by_phone_number(self, phone_number):
        return self.get(**{ 'phone_number': phone_number })
    
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=32, unique=True,
                                help_text=_(
                                    'Required. 30 ch'
                                ),
                                validators=[
                                    validators.RegexValidator(r'^[a-zA_Z][a-zA-Z0-9_\.]+$',
                                                              _('ss'), 'invalid')
                                ],
                                error_message={
                                    
                                }
                                )
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(_('nick_name'), max_length=150, blank=True)
    avatar = models.ImageField(_('avatar'), blank=True)
    birthday = models.DateField(_('gender'), help_text=_('femal is False, male is True, null is unset'))
    province = models.ForiegnKey(verbose_name=_('province'), to='Province', null=True, on_delete=models.SET_NULL)
    # email = models.EmailField(_('email address'), blank=True)
    # phone_number = models.BigIntegerField(_('mobile number'), null=True, blank=True,
    #                                       validators=[
    #                                           validators.RegexValidator(r'^989[0-3,9]\d{8}$',
    #                                                                     _('Enter a valid mobile number.', 'invalid'))
    #                                       ])

    class Meta():
        db_table = 'user_profiles'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


    @property
    def get_first_name(self):
        return self.user.first_name
    
    @property
    def get_last_name(self):
        return self.user.last_name