# -*- coding: gb18030 -*-
#
# $Id:Exp $

"""
持续性效果
"""

from Buff_Normal import Buff_Normal


class Buff_99003( Buff_Normal ):
	"""
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
		self.param1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" )  		#临时怪物列表Key
		self.param2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 			#使用后，保留几个怪物
		self.param3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) 			#使用距离
		self.param4 = 0
		self.param5 = 5
		
		if self.param2 == 0:
			self.param2 = 1
		
		if self.param1 == "":
			self.param1 = 'callMonstersTotal'
		
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
		self.param4 = receiver.queryTemp( self.param1, 0 )
		# self.param5 = receiver.queryTemp( 'callMonstersTimeTotal', 0 )
		receiver.setTemp( self.param1, self.param2 )	# 招怪个数
		receiver.setTemp( 'callMonstersTimeTotal', 3 )	# 招怪次数
		Buff_Normal.doBegin( self, receiver, buffData )
		
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
		self.param4 = receiver.queryTemp( self.param1, 0 )
		# self.param5 = receiver.queryTemp( 'callMonstersTimeTotal', 0 )
		receiver.setTemp( self.param1, self.param2 )	# 招怪个数
		receiver.setTemp( 'callMonstersTimeTotal', 3 )	# 招怪次数
		Buff_Normal.doReload( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.setTemp( self.param1, self.param4 )				# 招怪个数
		receiver.setTemp( 'callMonstersTimeTotal', self.param5 )	# 招怪次数
		Buff_Normal.doEnd( self, receiver, buffData )

