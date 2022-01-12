# -*- coding: gb18030 -*-
#

"""
飞行状态的buff by mushuang
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_6005 import Buff_6005
from csdefine import ROLE_FLAG_FLY, PET_WITHDRAW_BUFF

class Buff_8009( Buff_6005 ):
	"""
	此buff仅供坐骑使用，在其他地方使用会产生错误，详见Buff_Vehicle中的实现
	忽略场景是否允许飞行判断，用于GM指令
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_6005.__init__( self )
		
	def __setupEffect( self, receiver ):
		"""
		向receiver增加此buff的效果
		"""
		# 设定玩家为飞行标志
		receiver.addFlag( ROLE_FLAG_FLY )
		
		# 如果有出战宠物就收回宠物
		actPet = receiver.pcg_getActPet()
		if actPet:
			actPet.entity.withdraw( PET_WITHDRAW_BUFF )
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		# param1: 速度增加的百分比，例：如果需要速度增加50%，请将param1配置为50
		
		Buff_6005.init( self, dict )
		
		
		# 如果速度的增益百分比超过了最大值，那么修正为最大值
		if self.speedIncPercent > csconst.MAX_FLYING_SPEED_INC_PERCENT:
			self.speedIncPercent = csconst.MAX_FLYING_SPEED_INC_PERCENT
		
	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		Buff_6005.receive( self, caster, receiver )

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
		
		self.__setupEffect( receiver )
		
		# 增加移动速度并将骑宠buff加载到玩家身上
		Buff_6005.doBegin( self, receiver, buffData )

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
		self.__setupEffect( receiver )
		
		# 增加移动速度并将骑宠buff加载到玩家身上
		Buff_6005.doReload( self, receiver, buffData )
			
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		
		# 移除玩家身上的飞行标志
		receiver.removeFlag( ROLE_FLAG_FLY )
		
		# 恢复移动速度，并从玩家身上撤销所有骑宠buff
		Buff_6005.doEnd( self, receiver, buffData )


#
# $Log: not supported by cvs2svn $
#
#