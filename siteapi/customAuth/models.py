from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone
import jwt
import binascii
import os
from django.utils.translation import gettext_lazy as _


# Create your models here.


class ScuzzyFoxContentManagerUserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, jwt_auth_token=None, **extra_fields):
        username = username.lower()
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.email = email
        user.save(using=self._db)
        user.jwt_auth_token = CustomJWTToken.objects.create(user=user)
        return user


class ScuzzyFoxContentManagerUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    email = models.EmailField(null=False, blank=False)
    version = models.IntegerField(default=0)

    objects = ScuzzyFoxContentManagerUserManager()

    USERNAME_FIELD = 'username'

    EMAIL_FIELD = 'email'

    class Meta:
        verbose_name = 'ScuzzyFoxContentManagerUser'
        verbose_name_plural = 'ScuzzyFoxContentManagerUsers'

    def set_password(self, raw_password):
        self.version = self.version + 1
        try:
            self.jwt_auth_token.save()
        except Exception as e:
            print(e)
        super().set_password(raw_password)


class CustomJWTToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                primary_key=True, related_name='jwt_auth_token')
    key = models.CharField(max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        payload = {
            'id': self.user.id,
            'exp': timezone.now() + timezone.timedelta(days=60),
            'username': self.user.username,
            'version': self.user.version,
            'email': self.user.email
        }

        self.key = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        super(CustomJWTToken, self).save(*args, **kwargs)

    def __str__(self):
        return self.key


class TemporaryToken(models.Model):
    user = models.ForeignKey(
        ScuzzyFoxContentManagerUser, on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
