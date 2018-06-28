from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'

    # 启动发现
    #  该类是默认就存在的，我们在下面加入准备方法，
    #  扫描所有应用下的stark.py文件


    def ready(self):
        autodiscover_modules('stark')
        
        