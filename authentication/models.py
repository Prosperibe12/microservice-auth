from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    """ 
    Custom User Manager for user Class
    """
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required.
    """
    fullname = models.CharField(_("Your Fullname"), max_length=250, blank=False, null=False)
    email = models.EmailField(_("Email Address"), unique=True, blank=False, null=False)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_verified = models.BooleanField(
        _("Verified Status"),
        default=False,
        help_text=_("Designates whether the user is verified and can log into his/her account."),
    )
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    updated_at = models.DateTimeField(_("date updated"), auto_now=True)
    
    objects = MyUserManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    
    def __str__(self):
        return self.email
