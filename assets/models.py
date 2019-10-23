from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Asset(models.Model):
    """All Asset Table Definition"""

    # Defined choices for following columns
    # These two dimensions tuple is shown in the templates dropdown list.
    # get_COLUMNNAME_display() can get the second value of tuple
    # Please refer to this link for further information: http://www.liujiangblog.com/course/django/97
    asset_type_choice = (
        ('server', 'server'),
        ('networkdevice', 'network device'),
        ('storagedevice', 'storage device'),
        ('securitydevice', 'security device'),
        ('software', 'software'),
    )

    asset_status = (
        (0, 'online'),
        (1, 'offline'),
        (2, 'unknown'),
        (3, 'faulted'),
        (4, 'spare'),
    )

    # Define Simple Columns of Asset Table
    asset_type = models.CharField(choices=asset_type_choice, max_length=64, default='server', verbose_name='Asset Type')
    name = models.CharField(max_length=64, unique=True, verbose_name='Asset Name')
    sn = models.CharField(max_length=128, unique=True, verbose_name='Asset Serial Number')
    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name='Device Status')

    # Foreign Key
    # Params: (1) => Another Model Name;
    business_unit = models.ForeignKey('BusinessUnit', null=True, blank=True, verbose_name='Subordinated Business',
                                      on_delete=models.SET_Ngit ULL)
