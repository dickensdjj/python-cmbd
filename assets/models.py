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
    # sn and name attributes are unique
    asset_type = models.CharField(choices=asset_type_choice, max_length=64, default='server', verbose_name='Asset Type')
    name = models.CharField(max_length=64, unique=True, verbose_name='Asset Name')
    sn = models.CharField(max_length=128, unique=True, verbose_name='Asset Serial Number')
    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name='Device Status')
    manage_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Manage IP')
    purchase_day = models.DateField(null=True, blank=True, verbose_name='Purchase Day')
    expire_day = models.DateField(null=True, blank=True, verbose_name='Expire Day')
    price = models.FloatField(null=True, blank=True, verbose_name='Price')
    memo = models.TextField(null=True, blank=True, verbose_name='Memo')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='Approved Date')
    m_time = models.DateTimeField(auto_now=True, verbose_name='Updated Date')

    # Foreign Key Params: (1) => Another Model Name; First Argument without quote: it's a reference to a model either
    # defined within the file or imported via import; First Argument with quote:  Finding the model among all the
    # models in all installed apps related_name => reverse reference (反向引用); i.e. => manufacturer and cars:
    # manufacturer.related_name or default: manufacturer.modelname_set
    #
    # admin and approved by are using the same imported User, related name is used to distinguished them
    business_unit = models.ForeignKey('BusinessUnit', null=True, blank=True, verbose_name='Subordinated Business',
                                      on_delete=models.SET_NULL)
    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, verbose_name='Manufacturer',
                                     on_delete=models.SET_NULL)
    admin = models.ForeignKey(User, null=True, blank=True, verbose_name='Asset Manager', related_name='admin',
                              on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(User, null=True, blank=True, verbose_name='Approved By Whom',
                                    related_name='approved_by', on_delete=models.SET_NULL)
    idc = models.ForeignKey('IDC', null=True, blank=True, verbose_name='Machine Room', on_delete=models.SET_NULL)
    contract = models.ForeignKey('Contract', null=True, blank=True, verbose_name='Contract', on_delete=models.SET_NULL)

    # ManyToMany Fields
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Tag')

    # Refer to the asset_type tuple above
    def __str__(self):
        return '<%s> %s' % (self.get_asset_type_display(), self.name)

    # ???
    # These Meta class is used for admin/ ??? At least the first verbose name is shown as the db table name in admin/
    class Meta:
        verbose_name = 'Asset Main Table'
        verbose_name_plural = 'Asset Main Table'
        ordering = ['-c_time']


class Server(models.Model):
    """Server Device"""

    sub_asset_type_choice = (
        (0, 'PC Server'),
        (1, 'Blade Computer'),
        (2, 'Small Device'),
    )

    created_by_choice = (
        ('auto', 'Record Automatically'),
        ('manually', 'Record Manually'),
    )

    # One to One
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # server is the subset of assets

    # Define Columns
    sub_asset_type_choice = models.SmallIntegerField(choices=sub_asset_type_choice, default=0,
                                                     verbose_name='Server Type')
    created_by = models.CharField(choices=created_by_choice, max_length=32, default='auto', verbose_name='Record Mode')
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name='Server Model')
    raid_type = models.CharField(max_length=512, blank=True, null=True, verbose_name='Raid Type')
    os_type = models.CharField('OS Type', max_length=64, blank=True, null=True)
    os_distribution = models.CharField('Distribution', max_length=64, blank=True, null=True)
    os_release = models.CharField('OS Release', max_length=64, blank=True, null=True)

    # Foreign Key
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server', blank=True, null=True,
                                  verbose_name='Hosted Machine', on_delete=models.CASCADE)  # Virtual Machine

    def __str__(self):
        return '%s--%s--%s <sn: %s>' % \
               (self.asset.name, self.get_sub_asset_type_choice_display(), self.model, self.asset.sn)

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Server'


class SecurityDevice(models.Model):
    """Security Device"""

    sub_asset_choice = (
        (0, 'Firewall'),
        (1, 'Invade Device Detection'),
        (2, 'Internet Gateway'),
        (4, 'DevOps Audit System'),
    )

    # One to One
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)

    # Define Columns
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_choice, default=0, verbose_name='Security Asset Type')
    model = models.CharField(max_length=128, default='Unknown Model', verbose_name='Security Device Model')

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + "id:%s" % self.id

    class Meta:
        verbose_name = 'Security Device'
        verbose_name_plural = 'Security Device'


class StorageDevice(models.Model):
    """Storage Device"""

    sub_asset_type_choice = (
        (0, 'RIAD'),
        (1, 'Network Storage'),
        (2, 'Tape Library'),
        (4, 'Magnet Tape Unit'),
    )

    # One to One
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)

    # Define Columns
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0,
                                              verbose_name='Storage Device Type')
    model = models.CharField(max_length=128, default='Unknown Model', verbose_name='Storage Device Model')

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + "id:%s" % self.id

    class Meta:
        verbose_name = 'Storage Device'
        verbose_name_plural = "Storage Device"


class NetworkDevice(models.Model):
    """Network Device"""

    sub_asset_type_choice = (
        (0, 'Router'),
        (1, 'Switcher'),
        (2, 'LB'),
        (4, 'VPN Device'),
    )

    # One to One
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)

    # Define Columns
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0,
                                              verbose_name='Storage Device Type')
    vlan_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="VLanIP")
    intranet_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="Intranet IP")
    model = models.CharField(max_length=128, default='Unknown Model', verbose_name='Network Storage Device')
    firmware = models.CharField(max_length=128, blank=True, null=True, verbose_name='Device Firmware Model')
    port_num = models.SmallIntegerField(null=True, blank=True, verbose_name='The Number Of Port')
    device_detail = models.TextField(null=True, blank=True, verbose_name='Device Detail')

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + "id:%s" % self.id

    class Meta:
        verbose_name = 'Network Device'
        verbose_name_plural = "Network Device"


class Software(models.Model):
    """
    Save paid software only
    """

    sub_asset_type_choice = (
        (0, 'OS'),
        (1, 'Office/Development'),
        (2, 'Business'),
    )

    # Define Columns
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, null=True, blank=True,
                                              default=0, verbose_name='Software Type')
    license_num = models.IntegerField(default=1, verbose_name='License Amount')
    version = models.CharField(max_length=64, unique=True,
                               help_text='i.e. RedHat release 7 (Final)', verbose_name='Software/OS Version')

    def __str__(self):
        return '%s--%s' % (self.get_sub_asset_type_display(), self.version)

    class Meta:
        verbose_name = 'Software/OS'
        verbose_name_plural = 'Software/OS'


class IDC(models.Model):
    """Machine Room"""

    # Define Columns
    name = models.CharField(max_length=64, unique=True, verbose_name='IDC Name')
    memo = models.CharField(max_length=128, blank=True, null=True, verbose_name='Memo')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'IDC'
        verbose_name_plural = 'IDC'


class Manufacturer(models.Model):
    """Manufacturer"""

    # Define Columns
    name = models.CharField('Manufacturer Name', max_length=64, unique=True)
    telephone = models.CharField('Support Telephone', max_length=30, blank=True, null=True)
    memo = models.CharField('Memo', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Manufacturer'
        verbose_name_plural = 'Manufacturer'


class BusinessUnit(models.Model):
    """Business Unit(业务线)"""

    # Foreign Key
    parent_unit = models.ForeignKey('self', blank=True, null=True, related_name='parent_level',
                                    on_delete=models.SET_NULL)

    # Define Columns
    name = models.CharField('Business Unit', max_length=64, unique=True)
    memo = models.CharField('Memo', max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name;

    class Meta:
        verbose_name = 'Business Unit'
        verbose_name_plural = 'Business Unit'


class Contract(models.Model):
    """Contract"""

    # Define Columns
    sn = models.CharField('Contract Number', max_length=128, unique=True)
    name = models.CharField('contract Name', max_length=64)
    memo = models.TextField('Memo', blank=True, null=True)
    price = models.IntegerField('Contract Price')
    detail = models.TextField('Contract Detail', blank=True, null=True)
    start_day = models.DateField('Start Date', blank=True, null=True)
    end_day = models.DateField('End Date', blank=True, null=True)
    license_num = models.IntegerField('License Amount', blank=True, null=True)
    c_day = models.DateField('Created Date', auto_now_add=True)
    m_day = models.DateField('Modified Date', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Contract'
        verbose_name_plural = 'Contract'


class Tag(models.Model):
    """Tag"""

    # Define Columns
    name = models.CharField('Tag Name', max_length=32, unique=True)
    c_day = models.DateField('Created Date', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tag'


class CPU(models.Model):
    """CPU Component"""

    # One To One
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)

    # Define Columns
    cpu_model = models.CharField('CPU Model', max_length=128, blank=True, null=True)
    cpu_count = models.PositiveSmallIntegerField('Physical CPU Amount', default=1)
    cpu_core_count = models.PositiveSmallIntegerField('CPU Core Number', default=1)

    def __str__(self): return self.asset.name + ": " + self.cpu_model

    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = 'CPU'


class RAM(models.Model):
    """RAM Component"""

    # Foreign Key
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)

    # Define Columns
    sn = models.CharField('SN Number', max_length=128, blank=True, null=True)
    model = models.CharField('RAM Model', max_length=128, blank=True, null=True)
    manufacturer = models.CharField('RAM Manufacturer', max_length=128, blank=True, null=True)
    slot = models.CharField('Slot', max_length=64)
    capacity = models.IntegerField('RAM Size(GB)', blank=True, null=True)

    def __str__(self): return '%s: %s: %s: %s' % (self.asset.name, self.model, self.slot, self.capacity)

    class Meta:
        verbose_name = 'RAM'
        verbose_name_plural = 'RAM'
        # 内存的sn号可能无法获得, 就必须通过内存所在的插槽未知来唯一确定每条内存. 因此, unique_together = ('asset',
        # 'slot')这条设置非常关键, 相当于内存的主键了, 每条内存数据必须包含slot字段，否则就不合法.
        unique_together = ('asset', 'slot')


class Disk(models.Model):
    """Disk Device"""

    disk_interface_type_choice = (
        ('SATA', 'SATA'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
        ('unknown', 'unknown'),
    )

    # Foreign Key
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)

    # Define Columns
    sn = models.CharField('Disk SN Number', max_length=128)
    slot = models.CharField('Slot', max_length=64, blank=True, null=True)
    model = models.CharField('Disk Model', max_length=128, blank=True, null=True)
    manufacturer = models.CharField('Disk Manufacturer', max_length=128, blank=True, null=True)
    capacity = models.FloatField('Capacity', blank=True, null=True)
    interface_type = models.CharField('Interface Type', max_length=16, choices=disk_interface_type_choice,
                                      default='unknown')

    def __str__(self):
        return '%s:  %s:  %s:  %sGB' % (self.asset.name, self.model, self.slot, self.capacity)

    class Meta:
        verbose_name = 'Disk'
        verbose_name_plural = "Disk"
        unique_together = ('asset', 'sn')


class NIC(models.Model):
    """Network Interface Card"""

    # 1-m => asset - NIC
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)

    # Define Columns
    name = models.CharField('NIC Name', max_length=64, blank=True, null=True)
    model = models.CharField('NIC Model', max_length=128)
    mac = models.CharField('MAC', max_length=64)  # 虚拟机有可能会出现同样的mac地址
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    net_mask = models.CharField('Netmask', max_length=64, blank=True, null=True)
    bonding = models.CharField('Bound Address', max_length=64, blank=True, null=True)

    def __str__(self):
        return '%s:  %s:  %s' % (self.asset.name, self.model, self.mac)

    class Meta:
        verbose_name = 'NIC'
        verbose_name_plural = "NIC"
        unique_together = ('asset', 'model', 'mac')  # 资产、型号和mac必须联合唯一。防止虚拟机中的特殊情况发生错误。


class EventLog(models.Model):
    """
    Log.
    The log cannot be deleted when the related object is deleted.
    Therefore, on_delete=models.SET_NULL works for it.
    """

    name = models.CharField('Event Name', max_length=128)
    event_type_choice = (
        (0, 'Other'),
        (1, 'Hardware Update'),
        (2, 'Accessories Update'),
        (3, 'Device Offline'),
        (4, 'Device Online'),
        (5, 'Maintainese'),
        (6, 'Business Online/Update'),
    )

    # Foreign Key
    asset = models.ForeignKey('Asset', blank=True, null=True, on_delete=models.SET_NULL)
    new_asset = models.ForeignKey('NewAssetApprovalZone', blank=True, null=True,
                                  on_delete=models.SET_NULL)  # 当资产审批失败时有这项数据
    user = models.ForeignKey(User, blank=True, null=True, verbose_name='事件执行人',
                             on_delete=models.SET_NULL)  # 自动更新资产数据时没有执行人

    # Define columns
    event_type = models.SmallIntegerField('Event Type', choices=event_type_choice, default=4)
    component = models.CharField('Event Component', max_length=256, blank=True, null=True)
    detail = models.TextField('Event Detail')
    date = models.DateTimeField('Event Time', auto_now_add=True)
    memo = models.TextField('Memo', blank=True, null=True)

    def __str__(self): return self.name

    class Meta:
        verbose_name = "Event Log"
        verbose_name_plural = "Event Log"


class NewAssetApprovalZone(models.Model):
    """New Asset Approval Zone"""

    asset_type_choice = (
        ('server', 'Server'),
        ('networkdevice', 'Network Device'),
        ('storagedevice', 'Storage Device'),
        ('securitydevice', 'Security Device'),
        ('software', 'Software'),
    )

    # Define Columns
    sn = models.CharField('Asset SN Number', max_length=128, unique=True)
    asset_type = models.CharField(choices=asset_type_choice, default='server', max_length=64, blank=True, null=True,
                                  verbose_name='Asset Type')
    manufacturer = models.CharField(max_length=64, blank=True, null=True, verbose_name='Manufacturer')
    model = models.CharField(max_length=128, blank=True, null=True, verbose_name='Model')
    ram_size = models.PositiveIntegerField(blank=True, null=True, verbose_name='Capacity')
    cpu_model = models.CharField(max_length=128, blank=True, null=True, verbose_name='CPU Model')
    cpu_count = models.PositiveSmallIntegerField('CPU Amount', blank=True, null=True)
    cpu_core_count = models.PositiveSmallIntegerField('CPU Core Amount', blank=True, null=True)
    os_distribution = models.CharField('Distribution', max_length=64, blank=True, null=True)
    os_type = models.CharField('OS Type', max_length=64, blank=True, null=True)
    os_release = models.CharField('OS Release', max_length=64, blank=True, null=True)
    data = models.TextField('Asset Data')
    c_time = models.DateTimeField('Report Date', auto_now_add=True)
    m_time = models.DateTimeField('Data Update Date', auto_now=True)
    approved = models.BooleanField('Approval', default=False)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = 'New Asset Approval Zone'
        verbose_name_plural = "New Asset Approval Zone"
        ordering = ['-c_time']
