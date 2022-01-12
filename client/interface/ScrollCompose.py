# -*- coding: gb18030 -*-
"""
制作卷配方学习
"""
import event.EventCenter as ECenter
from ItemSystemExp import SpecialComposeExp
specom = SpecialComposeExp.instance()

class ScrollCompose:
	"""
	制作卷配方学习操作类
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		pass
		
	def onClientGetScrollSkill( self, sc ):
		"""
		学会一个配方
		"""
		
		ECenter.fireEvent( "EVT_ON_ROLE_GET_SCROLL_SKILL", sc, len( self.scrollSkill ) - 1 )
		
	def delScrollSkill( self, idx ):
		"""
		向服务器申请删除一个配方
		"""
		self.cell.sc_requestDelSkill( idx )
		
	def onDelScrollSkill( self, idx ):
		"""
		删除一个配方成功
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DEL_SCROLL_SKILL", idx )
	
	def onClientDecCount( self, idx ):
		"""
		配方使用次数减少
		"""
		pass
	
	def sc_getComposeCost( self, scrollID ):
		"""
		获取资金消耗
		"""
		return specom.getRequireMoney( scrollID )