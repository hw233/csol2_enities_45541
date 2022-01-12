# -*- coding: gb18030 -*-
#
# $Id: Buff_6005.py,v 1.1 2008-09-04 06:44:02 yangkai Exp $

"""
持续性效果
"""

from Buff_Vehicle import Buff_Vehicle
import Const
import csdefine
import csconst

class Buff_6005( Buff_Vehicle ):
	"""
	骑宠专用buff
	此buff仅供坐骑使用，在其他地方使用会产生错误，详见Buff_Vehicle中的实现
	example:移动速度提高%
	
	骑宠增加了BUFF数据结构，此数据结构交给基类处理，交给基类处理
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Vehicle.__init__( self )
		self.speedIncPercent = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Vehicle.init( self, dict )
		self.speedIncPercent = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0

	def springOnUseMaligSkill( self, caster, skill ):
		"""
		使用恶性技能被触发
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

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
		Buff_Vehicle.doBegin( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# 策划要求只有在没有骑宠的情况下才触发水域加速效果
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if receiver.isAccelerate:
					receiver.move_speed_value -= Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = False
		receiver.move_speed_percent += self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT
		receiver.calcMoveSpeed()
	
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
		Buff_Vehicle.doReload( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# 策划要求只有在没有骑宠的情况下才触发水域加速效果
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if receiver.isAccelerate:
					receiver.move_speed_value -= Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = False
		receiver.move_speed_percent += self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Vehicle.doEnd( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.removeOnUseMaligSkill( buffData[ "skill" ].getUID() )
		# 在水中下骑宠水域加速效果重新加载
		if hasattr( receiver, "onWaterArea" ):
			if receiver.onWaterArea:
				if not receiver.isAccelerate:
					receiver.move_speed_value += Const.WATER_SPEED_ACCELERATE
					receiver.isAccelerate = True
		receiver.move_speed_percent -= self.speedIncPercent * csconst.FLOAT_ZIP_PERCENT
		receiver.calcMoveSpeed()
		
# $Log: not supported by cvs2svn $