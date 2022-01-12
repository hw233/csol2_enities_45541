# -*- coding: gb18030 -*-

"""
实现不同语言版本的道具商城说明
"""
from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather

class deco_specialExplain( MultiLngFuncDecorator ):
	"""
	处理繁体版道具商城说明
	"""
	@staticmethod
	def locale_big5( SELF, pyTextPanel ) :
		"""
		BIG5 版本
		对于 BIG5 版本，有镶嵌水晶的分页
		"""
		pyTextPanel.text = labelGather.getText( "SpecialShop:explainwnd", "explain_big5" )