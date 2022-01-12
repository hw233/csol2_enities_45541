# -*- coding: gb18030 -*-

# 这个模块用于生成机器人测试任务应用实例

import appdata
from .templates import apply_template


def get_app_data( key, shouldReload = True ):
	if shouldReload:
		reload(appdata)
	return appdata.DATA[key]


def create_taskapp( key ):
	global _APP_DATAS

	try:
		return apply_template(*get_app_data(key))
	except Exception, err:
		print "Can't find task app data by key %s" % key
		print err

	return None
