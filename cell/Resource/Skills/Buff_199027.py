# -*- coding: gb18030 -*-
import BigWorld
from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine
import csconst

class Buff_199027( Buff_Normal ):
	"""
	拾取灵气副本状态

	在此状态中时，只允许使用左右键移动，其它操作无效
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.decRewardValue = 0.0 #减少奖励潜能点的数据

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.decRewardValue = float( float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) )

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
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setTemp( "decRewardPotential", self.decRewardValue )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "decRewardPotential", self.decRewardValue )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "decRewardPotential" )