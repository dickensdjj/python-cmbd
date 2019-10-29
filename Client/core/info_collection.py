import sys
import platform


class InfoCollection(object):

    def collect(self):
        # Collect Platform Info
        # 首先判断当前平台，根据平台的不同，执行不同的方法
        try:
            func = getattr(self, platform.system().lower())
            info_data = func()
            formatted_data = self.build_report_data(info_data)
            return formatted_data
        except AttributeError:
            sys.exit("Program does not support current system: [%s]! " % platform.system())

    @staticmethod
    def linux():
        from plugins.collect_linux_info import collect
        return collect()

    @staticmethod
    def darwin():
        from plugins.collect_darwin_info import collect
        return collect()

    @staticmethod
    def windows():
        from plugins.collect_window_info import collect
        return collect()

    @staticmethod
    def build_report_data(data):
        # 留下一个接口, 方便增加功能或者过滤数据
        pass
        return data
