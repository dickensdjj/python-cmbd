import json
from assets import models


class NewAsset(object):
    def __init__(self, request, data):
        self.request = request
        self.data = data

    def add_to_new_assets_zone(self):
        defaults = {
            'data': json.dumps(self.data),
            'asset_type': self.data.get('asset_type'),
            'manufacturer': self.data.get('manufacturer'),
            'model': self.data.get('model'),
            'ram_size': self.data.get('ram_size'),
            'cpu_model': self.data.get('cpu_model'),
            'cpu_count': self.data.get('cpu_count'),
            'cpu_core_count': self.data.get('cpu_core_count'),
            'os_distribution': self.data.get('os_distribution'),
            'os_release': self.data.get('os_release'),
            'os_type': self.data.get('os_type'),
        }
        # Each models has one manager, which named objects as default
        models.NewAssetApprovalZone.objects.update_or_create(sn=self.data['sn'], defaults=defaults)
        return 'Asset has been added or updated to new asset approval zone.'

    def log(log_type, msg=None, asset=None, new_asset=None, request=None):
        """
        Log Recording
        :param msg:
        :param asset:
        :param new_asset:
        :param request:
        :return:
        """

        event = models.EventLog()
        if log_type == 'upline':
            event.name = "%s <%s>: upline" % (asset.name, asset.sn)
            event.asset = asset
            event.detail = 'Asset has been uplined successfully'
            event.user = request.user
        elif log_type == 'approved_failed':
            event.name = "%s <%s>: Approved Failed" % (new_asset.asset_type, new_asset.sn)
            event.new_asset = new_asset
            event.detail = "Approved Failed! \n%s" % (msg)
            event.user = request.user
        elif log_type == 'update':
            event.name = '%s <%s>: Info Update' % (asset.asset_type, asset.sn)
            event.asset = asset
            event.detail = 'Update Successfully'

        elif log_type == "update_failed":
            event.name = "%s <%s>: Updated Failed" % (asset.asset_type, asset.sn)
            event.asset = asset
            event.detail = "Update Failed! \n%s" % (msg)

        event.save()


class ApprovedAsset:
    """
    Asset approve and upline
    """

    def __init__(self, request, asset_id):
        self.request = request
        self.new_asset = models.NewAssetApprovalZone.objects.get(id=asset_id)
        self.data = json.loads(self.new_asset.data)

    def asset_upline(self):
        func = getattr(self, "_%s_upline" % self.new_asset.asset_type)
        ret = func()
        return ret

    def _server_upline(self):
        asset = self._create_asset()
        try:
            self._create_manufacturer(asset)
            self._create_server(asset)
            self._create_CPU(asset)
            self._create_RAM(asset)
            self._create_nic(asset)
            self._delete_original_asset()
        except Exception as e:
            asset.delete()
            NewAsset.log('approved_failed', msg=e, new_asset=self.new_asset, request=self.request)
            print(e)
            return False
        else:
            NewAsset.log("upline", asset=asset, request=self.request)
            print('New server uplined!')
            return True

    def _create_asset(self):
        """
        Create Asset and Upline
        :return:
        """

        asset = models.Asset.objects.create(asset_type=self.new_asset.asset_type,
                                            name="%s: %s" % (self.new_asset.asset_type, self.new_asset.sn),
                                            sn=self.new_asset.sn,
                                            approved_by=self.request.user
                                            )

        return asset

    def _create_manufacturer(self, asset):
        """
        create manufacturer
        :param asset:
        :return:
        """
        m = self.new_asset.manufacturer
        if m:
            manufacturer_obj, _ = models.Manufacturer.objects.get_or_create(name=m)
            asset.manufacturer = manufacturer_obj
            asset.save()

    def _create_server(self, asset):
        """
        Create Server
        :param asset:
        :return:
        """

        models.Server.objects.create(asset=asset,
                                     model=self.new_asset.model,
                                     os_type=self.new_asset.os_type,
                                     os_distribution=self.new_asset.os_distribution,
                                     os_release=self.new_asset.os_release,
                                     )

    def _create_CPU(self, asset):
        """
        Create CPU
        :param asset:
        :return:
        """

        cpu = models.CPU.objects.create(asset=asset)
        cpu.cpu_model = self.new_asset.cpu_model
        cpu.cpu_count = self.new_asset.cpu_count
        cpu.cpu_core_count = self.new_asset.cpu_core_count
        cpu.save()

    def _create_RAM(self, asset):
        """
        Create RAM. More than 1 RAM generally
        :param asset:
        :return:
        """

        ram_list = self.data.get('ram')
        if not ram_list:
            return
        for ram_dict in ram_list:
            if not ram_dict.get('slot'):
                raise ValueError('Unknown Slot')
            ram = models.RAM()
            ram.asset = asset
            ram.slot = ram_dict.get('slot')
            ram.model = ram_dict.get('model')
            ram.manufacturer = ram_dict.get('manufacturer')
            ram.capacity = ram_dict.get('capacity', 0)
            ram.save()

    def _create_disk(self, asset):

        disk_list = self.data.get('physical_disk_driver')
        if not disk_list:
            return
        for disk_dict in disk_list:
            if not disk_dict.get('sn'):
                raise ValueError("未知sn的硬盘！")  # 根据sn确定具体某块硬盘。
            disk = models.Disk()
            disk.asset = asset
            disk.sn = disk_dict.get('sn')
            disk.model = disk_dict.get('model')
            disk.manufacturer = disk_dict.get('manufacturer'),
            disk.slot = disk_dict.get('slot')
            disk.capacity = disk_dict.get('capacity', 0)
            iface = disk_dict.get('interface_type')
            if iface in ['SATA', 'SAS', 'SCSI', 'SSD', 'unknown']:
                disk.interface_type = iface

            disk.save()

    def _create_nic(self, asset):
        """
        创建网卡。可能有多个网卡，甚至虚拟网卡。
        :param asset:
        :return:
        """
        nic_list = self.data.get("nic")
        if not nic_list:
            return

        for nic_dict in nic_list:
            if not nic_dict.get('mac'):
                raise ValueError("网卡缺少mac地址！")
            if not nic_dict.get('model'):
                raise ValueError("网卡型号未知！")

            nic = models.NIC()
            nic.asset = asset
            nic.name = nic_dict.get('name')
            nic.model = nic_dict.get('model')
            nic.mac = nic_dict.get('mac')
            nic.ip_address = nic_dict.get('ip_address')
            if nic_dict.get('net_mask'):
                if len(nic_dict.get('net_mask')) > 0:
                    nic.net_mask = nic_dict.get('net_mask')[0]
            nic.save()

    def _delete_original_asset(self):
        """
        这里的逻辑是已经审批上线的资产，就从待审批区删除。
        也可以设置为修改成已审批状态但不删除，只是在管理界面特别处理，不让再次审批，灰色显示。
        不过这样可能导致待审批区越来越大。
        :return:
        """
        self.new_asset.delete()


class UpdateAsset:
    """
    Auto Update online asset
    """

    def __init__(self, request, asset, report_data):
        self.request = request
        self.asset = asset
        self.report_data = report_data
        self.asset_update()

    def asset_update(self):
        func = getattr(self, "_%s_update" % self.report_data['asset_type'])
        ret = func()
        return ret

    def _server_update(self):
        try:
            self._update_manufacturer()  # 更新厂商
            self._update_server()  # 更新服务器
            self._update_CPU()  # 更新CPU
            self._update_RAM()  # 更新内存
            self._update_disk()  # 更新硬盘
            self._update_nic()  # 更新网卡
            self.asset.save()
        except Exception as e:
            NewAsset.log('update_failed', msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            NewAsset.log("update", asset=self.asset)
            print("资产数据被更新!")
            return True

    def _update_manufacturer(self):
        """
        更新厂商
        """
        m = self.report_data.get('manufacturer')
        if m:
            manufacturer_obj, _ = models.Manufacturer.objects.get_or_create(name=m)
            self.asset.manufacturer = manufacturer_obj
        else:
            self.asset.manufacturer = None
        self.asset.manufacturer.save()

    def _update_server(self):
        """
        更新服务器
        """
        self.asset.server.model = self.report_data.get('model')
        self.asset.server.os_type = self.report_data.get('os_type')
        self.asset.server.os_distribution = self.report_data.get('os_distribution')
        self.asset.server.os_release = self.report_data.get('os_release')
        self.asset.server.save()

    def _update_CPU(self):
        """
        更新CPU信息
        :return:
        """
        self.asset.cpu.cpu_model = self.report_data.get('cpu_model')
        self.asset.cpu.cpu_count = self.report_data.get('cpu_count')
        self.asset.cpu.cpu_core_count = self.report_data.get('cpu_core_count')
        self.asset.cpu.save()

    def _update_RAM(self):
        """
        更新内存信息。
        使用集合数据类型中差的概念，处理不同的情况。
        如果新数据有，但原数据没有，则新增；
        如果新数据没有，但原数据有，则删除原来多余的部分；
        如果新的和原数据都有，则更新。
        在原则上，下面的代码应该写成一个复用的函数，
        但是由于内存、硬盘、网卡在某些方面的差别，导致很难提取出重用的代码。
        :return:
        """
        # 获取已有内存信息，并转成字典格式
        old_rams = models.RAM.objects.filter(asset=self.asset)
        old_rams_dict = dict()
        if old_rams:
            for ram in old_rams:
                old_rams_dict[ram.slot] = ram
        # 获取新数据中的内存信息，并转成字典格式
        new_rams_list = self.report_data['ram']
        new_rams_dict = dict()
        if new_rams_list:
            for item in new_rams_list:
                new_rams_dict[item['slot']] = item

        # 利用set类型的差集功能，获得需要删除的内存数据对象
        need_deleted_keys = set(old_rams_dict.keys()) - set(new_rams_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_rams_dict[key].delete()

                # 需要新增或更新的
                if new_rams_dict:
                    for key in new_rams_dict:
                        defaults = {
                            'sn': new_rams_dict[key].get('sn'),
                            'model': new_rams_dict[key].get('model'),
                            'manufacturer': new_rams_dict[key].get('manufacturer'),
                            'capacity': new_rams_dict[key].get('capacity', 0),
                        }
                        models.RAM.objects.update_or_create(asset=self.asset, slot=key, defaults=defaults)

    def _update_disk(self):
        """
        更新硬盘信息。类似更新内存。
        """
        old_disks = models.Disk.objects.filter(asset=self.asset)
        old_disks_dict = dict()
        if old_disks:
            for disk in old_disks:
                old_disks_dict[disk.sn] = disk

        new_disks_list = self.report_data['physical_disk_driver']
        new_disks_dict = dict()
        if new_disks_list:
            for item in new_disks_list:
                new_disks_dict[item['sn']] = item

        # 需要删除的
        need_deleted_keys = set(old_disks_dict.keys()) - set(new_disks_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_disks_dict[key].delete()
                # 需要新增或更新的
                if new_disks_dict:
                    for key in new_disks_dict:
                        interface_type = new_disks_dict[key].get('interface_type', 'unknown')
                        if interface_type not in ['SATA', 'SAS', 'SCSI', 'SSD', 'unknown']:
                            interface_type = 'unknown'
                        defaults = {
                            'slot': new_disks_dict[key].get('slot'),
                            'model': new_disks_dict[key].get('model'),
                            'manufacturer': new_disks_dict[key].get('manufacturer'),
                            'capacity': new_disks_dict[key].get('capacity', 0),
                            'interface_type': interface_type,
                        }
                        models.Disk.objects.update_or_create(asset=self.asset, sn=key, defaults=defaults)

    def _update_nic(self):
        """
        更新网卡信息。类似更新内存。
        """
        old_nics = models.NIC.objects.filter(asset=self.asset)
        old_nics_dict = dict()
        if old_nics:
            for nic in old_nics:
                old_nics_dict[nic.model + nic.mac] = nic

        new_nics_list = self.report_data['nic']
        new_nics_dict = dict()
        if new_nics_list:
            for item in new_nics_list:
                new_nics_dict[item['model'] + item['mac']] = item

        # 需要删除的
        need_deleted_keys = set(old_nics_dict.keys()) - set(new_nics_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_nics_dict[key].delete()

                # 需要新增或更新的
                if new_nics_dict:
                    for key in new_nics_dict:
                        if new_nics_dict[key].get('net_mask') and len(new_nics_dict[key].get('net_mask')) > 0:
                            net_mask = new_nics_dict[key].get('net_mask')[0]
                        else:
                            net_mask = ""
                        defaults = {
                            'name': new_nics_dict[key].get('name'),
                            'ip_address': new_nics_dict[key].get('ip_address'),
                            'net_mask': net_mask,
                        }
                        models.NIC.objects.update_or_create(asset=self.asset, model=new_nics_dict[key]['model'],
                                                            mac=new_nics_dict[key]['mac'], defaults=defaults)

        print('更新成功！')
