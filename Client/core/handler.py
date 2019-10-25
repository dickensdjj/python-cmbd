import json
import time
import urllib.parse
import urllib.request
from core import info_collection
from conf import settings


class ArgvHandler(object):

    def __init__(self, args):
        self.args = args
        self.parse_args()

    def parse_args(self):
        """
        分析参数, 如果参数有制定方法, 执行功能, 如果没有则打印说明
        :return:
        """

        if len(self.args) > 1 and hasattr(self, self.args[1]):
            func = getattr(self, self.args[1])
            func()
        else:
            self.help_msg()

    # 以上实例声明了静态方法 help_msg，从而可以实现实例化使用 ArgHandler().help_msg()，当然也可以不实例化调用该方法 ArgHandler.help_msg()。
    @staticmethod
    def help_msg():
        """
        Print Menu
        :return:
        """

        msg = '''
        参数名               功能

        collect_data        测试收集硬件信息的功能

        report_data         收集硬件信息并汇报
        '''
        print(msg)

    @staticmethod
    def collect_data():
        """
        Collect Device Info, used for testing
        :return:
        """

        info = info_collection.InfoCollection()
        asset_data = info.collect()
        print(asset_data)

    @staticmethod
    def report_data():
        """
        Collect Device Info, send to server
        :return:
        """

        # Collect
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        # Pack info in dict and convert to json format
        data = {"asset_data": json.dump(asset_data)}
        url = "http://%s:%s%s" % (settings.Params['server'], settings.Params['port'], settings.Params['url'])
        print('Sending data to : [%s] ...... ' % url)
        try:
            # use builtin urllib.request lib to send post request
            # encode data and convert to bytes
            data_encode = urllib.parse.urlencode(data).encode()
            response = urllib.request.urlopen(url=url, data=data_encode, timeout=settings.Params['request_timeout'])
            # ???
            print("\033[31;1mSend Complete! \033[0m ")
        except Exception as e:
            # ???
            message = 'Send Failed' + "  Error:  {}".format(e)
            print("\033[31;1mSend Failed, Error: %s\033[0m" % e)
        # ???
        with open(settings.PATH, 'ab') as f:
            log = 'Send Time: %s \t Server Address: %s \t Response: %s \n' % (time.strftime('%Y-%m-%d %H:%M:%S'), url, message)
            f.write(log.encode())
            print("Log has been successfully recorded")
