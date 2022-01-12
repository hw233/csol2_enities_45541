# -*- coding: gb18030 -*-
#
# $Id: Buff_22005.py,v 1.2 2008-08-05 08:44:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Normal import Buff_Normal
import random
import csconst
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_99010( Buff_Normal ):
	"""
	example:骑宠传送	BUFF	角色在此期间不会被攻击， 不会被玩家控制， 坐上飞行模型
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.patrolPathNode = ""
		self.patrolList = ""
		self.spaceName = ""
		self.pos = ( 0, 0, 0 )
		self.direction = ( 0, 0, 0 )
		self.isSuccess = False
		self.isStop = False

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 3 # 强制3秒检测一次, 因为我们需要记录当前的巡逻点

	def continuePatrol( self, receiver ):
		"""
		继续巡逻 角色跳转场景后 场景加载完毕继续巡逻
		"""
		DEBUG_MSG( "continuePatrol----->patrol data!", self.patrolPathNode, self.patrolList, \
		self.spaceName, self.pos, self.direction )

		self.isStop = False
		patrolList = BigWorld.PatrolPath( self.patrolList )
		if patrolList.isReady():
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )

	def updateData( self, receiver ):
		"""
		更新巡逻数据
		"""
		receiver.stopMoving()
		self.isSuccess = False
		self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction = receiver.queryTemp( "teleportFly_data" )
		patrolList = BigWorld.PatrolPath( self.patrolList )
		if patrolList.isReady():
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )
		return


		receiver.stopMoving()
		self.isStop = True
		self.isSuccess = False
		self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction = receiver.queryTemp( "teleportFly_data" )
		receiver.doPatrol( self.patrolPathNode, patrolList )
		receiver.stopMoving()
		DEBUG_MSG( "updateData----->patrol data!", self.patrolPathNode, self.patrolList, \
		self.spaceName, self.pos, self.direction )

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #是恶性但不是光环效果 那么免疫
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # 是光环效果
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
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
		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# 骑乘下马
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		receiver.addFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )

		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateInc( csdefine.EFFECT_STATE_ALL_NO_FIGHT )
		receiver.setTemp( "controlledBy_bck", receiver.controlledBy )

		receiver.controlledBy = None
		patrolPathNode, patrolList, spaceName, pos, direction = receiver.queryTemp( "teleportFly_data" )

		dctData = { "param" : { "patrolPathNode" 	: patrolPathNode, 	"patrolList" 		: patrolList, \
								 "spaceName" 		: spaceName, 		"pos" 				: pos, \
								 "direction" 		: direction,		"isSuccess" 		: False, \
							 	 "isStop"			: False,
							 }
					}

		buffData[ "skill" ] = self.createFromDict( dctData )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		patrolPath = BigWorld.PatrolPath( patrolList )

		if patrolPath.isReady():
			buffData[ "skill" ].isSuccess = receiver.doPatrol( patrolPathNode, patrolPath )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		if receiver.popTemp( "fly_buff_exit", 0 ) == self.getID():
			return False

		if not self.isStop:
			if self.isSuccess:
				patrolPathNode = receiver.queryTemp( "patrolPathNode" )
				if patrolPathNode is None:
					self.isSuccess = False
					return Buff_Normal.doLoop( self, receiver, buffData )

				self.patrolPathNode = patrolPathNode
			else:
				patrolList = BigWorld.PatrolPath( self.patrolList )
				if patrolList.isReady():
					self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )
				else:
					DEBUG_MSG( "im do not patrol!" )

		return Buff_Normal.doLoop( self, receiver, buffData )

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
		receiver.setTemp( "fly_buff_exit", self.getID() )

		# 暂时不实现上线后继续巡逻
		receiver.setTemp( "no_continue", self.getID() )
		receiver.gotoSpace( self.spaceName, self.pos, self.direction )
		return

		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateInc( csdefine.EFFECT_STATE_ALL_NO_FIGHT )

		receiver.setTemp( "controlledBy_bck", receiver.controlledBy )
		receiver.controlledBy = None

		try:
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, BigWorld.PatrolPath( self.patrolList ) )
		except:
			DEBUG_MSG( "%i doPatrol is failed! patrolPathNode=%s, patrolList=%s" % ( receiver.id, self.patrolPathNode, self.patrolList ) )
			receiver.removeBuffByID( self.getID(), [0] )
			receiver.gotoSpace( self.spaceName, self.pos, self.direction )

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
		Buff_Normal.doEnd( self, receiver, buffData )
		# 暂时不实现上线后继续巡逻
		if receiver.popTemp( "no_continue", 0 ) == self.getID():
			return

		fly_model_add_speed = receiver.queryTemp( "fly_model_add_speed", 0 )
		if fly_model_add_speed > 0:
			receiver.move_speed_value -= fly_model_add_speed
			receiver.removeTemp( "fly_model_add_speed" )
			receiver.calcMoveSpeed()

		receiver.vehicleModelNum = 0	# 先设置vehicleModelNum
		receiver.removeFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateDec( csdefine.EFFECT_STATE_ALL_NO_FIGHT )
		receiver.stopMoving()
		receiver.controlledBy = receiver.popTemp( "controlledBy_bck" )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "patrolPathNode" 	: self.patrolPathNode, \
							 "patrolList" 		: self.patrolList, \
							 "spaceName" 		: self.spaceName, \
							 "pos" 				: self.pos, \
							 "direction" 		: self.direction,\
							 "isSuccess" 		: self.isSuccess,\
							 "isStop"			: self.isStop
				 			}
				 }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_99010()
		obj.__dict__.update( self.__dict__ )

		obj.patrolPathNode = data["param"][ "patrolPathNode" ]
		obj.patrolList = data["param"][ "patrolList" ]
		obj.spaceName = data["param"][ "spaceName" ]
		obj.pos = data["param"][ "pos" ]
		obj.direction = data["param"][ "direction" ]
		obj.isSuccess = data["param"][ "isSuccess" ]
		obj.isStop = data["param"][ "isStop" ]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/05 06:36:02  kebiao
# no message
#
#
#