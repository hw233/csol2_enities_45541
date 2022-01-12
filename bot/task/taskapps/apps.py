# -*- coding: gb18030 -*-

# ���ģ���������ɻ����˲�������Ӧ��ʵ��

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
