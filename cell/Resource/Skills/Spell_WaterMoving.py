# -*- coding:gb18030 -*-

#edit by wuxo 2012-8-31
import csdefine
from Spell_BuffNormal import Spell_BuffNormal
import csstatus
from VehicleHelper import getCurrVehicleID

class Spell_WaterMoving( Spell_BuffNormal):
	"""
	轻功系统-触发迅捷移动buff的技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.needEnergy = 0
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.needEnergy = int( data["buff"][0]["Param2"] )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#if getCurrVehicleID( caster ): # 坐骑无法释放轻功技能
		#	return csstatus.SKILL_NO_MSG 
		if caster.energy < self.needEnergy or caster.getState() == csdefine.ENTITY_STATE_FIGHT : #判断跳跃能量值
			return csstatus.SKILL_NO_MSG 
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.findBuffByBuffID(22130):
			return
		self.receiveLinkBuff( caster, receiver )

