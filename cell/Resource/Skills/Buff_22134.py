# -*- coding: gb18030 -*-
#替换玩家技能

"""
持续性效果
"""

# bigworld
import ResMgr
import BigWorld
# common
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID
# cell
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_22134( Buff_Normal ):
	"""
	替换玩家技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.replaceSkills = []		# 获得buff后，玩家只能使用这些技能
		self.flag = 0 #是否判断空间技能
		self.notUseSelfSkill = 0 #是否不能使用自己的技能

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		skills = dict["Param1"].split(";")
		self.replaceSkills = [ int( i ) for i in skills ]
		if dict["Param2"]!="":
			self.flag = int( dict["Param2"] )
		if dict["Param3"]!="":
			self.notUseSelfSkill = int( dict["Param3"] )

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		if buff.isRayRingEffect() :						# 是光环效果
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST
		elif buff.isMalignant() :						# 是恶性但不是光环效果 那么免疫
			return csstatus.SKILL_BUFF_IS_RESIST
		return csstatus.SKILL_GO_ON

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
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗

		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# 骑乘下马
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		if self.replaceSkills :
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# 替换玩家技能栏
	
	def doReload( self, receiver, buffData ):
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		
		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )
		
		if self.replaceSkills :
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# 替换玩家技能栏

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
		receiver.removeTemp( "FLY_TEL_SKILL_FLAG" )
		receiver.removeTemp( "NOT_USE_SELF_SKILL_FLAG" )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		if self.replaceSkills :
			receiver.client.onCloseCopySpaceInterface()# 通知技能列表更换

