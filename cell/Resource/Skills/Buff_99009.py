# -*- coding: gb18030 -*-

"""
改变摆摊招牌编号buff，buff结束后改变为自由状态
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99009( Buff_Normal ):
	"""
	改变摆摊招牌编号buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._vendSignboardNumber = ""
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._vendSignboardNumber = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# 技能对应的摆摊招牌编号
		
	def doBegin( self, receiver, buffData ):
		"""
		更换摆摊招牌编号
		"""
		receiver.vendSignboardNumber = self._vendSignboardNumber
		
		Buff_Normal.doBegin( self, receiver, buffData )
	
	def doReload( self, receiver, buffData ):
		"""
		更换摆摊招牌编号
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.vendSignboardNumber = self._vendSignboardNumber
	
	def doEnd( self, receiver, buffData ):
		"""
		更换摆摊招牌编号
		"""
		receiver.vendSignboardNumber = ""
		
		Buff_Normal.doEnd( self, receiver, buffData )
		