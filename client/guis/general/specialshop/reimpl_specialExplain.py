# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾�ĵ����̳�˵��
"""
from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather

class deco_specialExplain( MultiLngFuncDecorator ):
	"""
	�����������̳�˵��
	"""
	@staticmethod
	def locale_big5( SELF, pyTextPanel ) :
		"""
		BIG5 �汾
		���� BIG5 �汾������Ƕˮ���ķ�ҳ
		"""
		pyTextPanel.text = labelGather.getText( "SpecialShop:explainwnd", "explain_big5" )