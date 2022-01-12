# -*- coding: gb18030 -*-
#
# 骑上坐骑攻击，并沿指定路线巡逻，并限定玩家使用指定的技能
# by ganjinxing 2011-11-26

#对飞行路线进行曲线化 移到客户端进行 modify by wuxo 2012-3-2

"""
持续性效果
"""

# bigworld
import Math
import ResMgr
import BigWorld
# common
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID
# cell
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET


class Buff_299032( Buff_Normal ):
	"""
	example:骑宠传送	BUFF	角色在此期间不会被攻击， 不会被玩家控制， 坐上飞行模型
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.replaceSkills = []		# 获得buff后，玩家只能使用这些技能
		self.max_speed     =  0.0	#在此状态下允许的最大速度
		self.requestSkills = []		#在飞行中可能播放的技能列表
		self.flag = 0 #是否判断空间技能
		self.notUseSelfSkill = 0 #是否不能使用自己的技能
		self.flyPos = ()	# 起飞初始位置

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		skills = dict["Param1"].split(";")
		if len( skills ) > 1 :
			self.replaceSkills = eval( skills[0] )
			self.requestSkills = eval( skills[1] )
		if len( skills ) > 2 :
			self.flag = int( skills[2] )
		if len( skills ) > 3 :
			self.notUseSelfSkill = int( skills[3] )

		flyInfos = str( dict[ "Param3" ] ).split(";") 
		if len(flyInfos) > 2:
			self.max_speed = float(flyInfos[2])

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
		receiver.setTemp( "TEL_SKILLS", self.requestSkills )
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.move_speed = self.max_speed
		receiver.updateTopSpeed()
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗

		if not self.flyPos:	# 记录起飞初始位置
			self.flyPos = Math.Vector3( receiver.position )

		actPet = receiver.pcg_getActPet()
		if actPet:
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# 骑乘下马
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		receiver.addFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )

		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )

		if self.replaceSkills:
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# 替换玩家技能栏

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
		# 暂时不实现上线后继续巡逻
		Buff_Normal.doReload( self, receiver, buffData )
		if self.flyPos:	# 回到初始位置
			receiver.position = self.flyPos
		# 然后结束掉buff
		receiver.removeBuffByBuffID( self._buffID, [csdefine.BUFF_INTERRUPT_NONE] )

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
		receiver.vehicleModelNum = 0	# 先设置vehicleModelNum
		receiver.removeFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		if self.replaceSkills:
			receiver.client.onCloseCopySpaceInterface()							# 通知技能列表更换
		receiver.calcMoveSpeed()
		receiver.removeTemp( "TEL_SKILLS" )
		receiver.removeTemp( "FLY_TEL_SKILL_FLAG" )
		receiver.removeTemp( "NOT_USE_SELF_SKILL_FLAG" )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		if self.getUID() == 0:
			self.setUID( newUID() )

		return { "param": { "flyPos" : self.flyPos, "uid" : self.getUID() } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_299032()
		obj.__dict__.update( self.__dict__ )
		obj.flyPos = data["param"]["flyPos"]

		if not data.has_key( "uid" ) or data["uid"] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data["uid"] )
		return obj
