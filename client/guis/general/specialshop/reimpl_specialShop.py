# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾�ĵ����̳ǽ���

2010.05.11: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_guispecialShopStart( MultiLngFuncDecorator ) :
	"""
	������Ƕˮ����ť����ʾ״̬
	"""
	@staticmethod
	def locale_big5( SELF, wnd ) :
		"""
		BIG5 �汾
		���� BIG5 �汾������Ƕˮ���ķ�ҳ
		"""
		wnd.tabCtrl.typeBtn_10.visible = True
		wnd.tabCtrl.typeBtn_11.visible = False

class deco_guispecialShopOnCharge( MultiLngFuncDecorator ) :
	"""
	��ֵ��ť�����¼�
	"""
	@staticmethod
	def locale_big5( SELF ) :
		"""
		BIG5 �汾
		���� BIG5 �汾Ӧ�ô�������ҳ
		"""
		import csol
		csol.openUrl( "http://gamemall.wayi.com.tw/shopping/default.asp?action=wgs_list " )
