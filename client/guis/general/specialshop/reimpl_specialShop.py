# -*- coding: gb18030 -*-

"""
实现不同语言版本的道具商城界面

2010.05.11: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_guispecialShopStart( MultiLngFuncDecorator ) :
	"""
	处理镶嵌水晶按钮的显示状态
	"""
	@staticmethod
	def locale_big5( SELF, wnd ) :
		"""
		BIG5 版本
		对于 BIG5 版本，有镶嵌水晶的分页
		"""
		wnd.tabCtrl.typeBtn_10.visible = True
		wnd.tabCtrl.typeBtn_11.visible = False

class deco_guispecialShopOnCharge( MultiLngFuncDecorator ) :
	"""
	充值按钮触发事件
	"""
	@staticmethod
	def locale_big5( SELF ) :
		"""
		BIG5 版本
		对于 BIG5 版本应该触发的网页
		"""
		import csol
		csol.openUrl( "http://gamemall.wayi.com.tw/shopping/default.asp?action=wgs_list " )
