# -*- coding: gb18030 -*-
#
# 防沉迷系统之 疲劳 debuff 2009-03-20 SongPeifang
#

from Buff_Normal import Buff_Normal

class Buff_299009( Buff_Normal ):
	"""
	防沉迷系统之 疲劳debuff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		receiver.setTemp( "anti_indulgence_tired", True )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		receiver.setTemp( "anti_indulgence_tired", True )
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		"""
		# 清除掉疲劳的标记
		receiver.removeTemp( "anti_indulgence_tired" )