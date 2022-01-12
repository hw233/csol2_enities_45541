# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
持续性效果
"""
import random
import Math
import BigWorld

import csstatus
import csdefine
from bwdebug import *
from Function import newUID

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_108006( Buff_Normal ):
	"""
	example:使目标变为一只青蛙，不受控制，无法使用技能，受到攻击时恢复，持续20秒。被变形期间，目标将每秒恢复10%的生命和法力。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.isEnd = False
		self.currModelNumber = ""
		self.currModelScale = 1.0
		#self.__targetPos = () # 保存对象初始位置，变成青蛙后在以初始位置为中心一定范围内随机走动。

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = dict[ "Param1" ]
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) / 100.0
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) / 100.0

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
		receiver.setHP( receiver.HP + receiver.HP_Max * self._p3 )
		receiver.setMP( receiver.MP + receiver.MP_Max * self._p3 )
		
		if not ( receiver.effect_state & csdefine.EFFECT_STATE_BE_HOMING ) :
			if not receiver.queryTemp( "BODY_CHANGE_POS", None ):
				receiver.setTemp( "BODY_CHANGE_POS", Math.Vector3( receiver.position ) )
			receiver.doRandomRun( receiver.queryTemp( "BODY_CHANGE_POS" ), 5.0 ) # 在一定范围内随机走动
		else:
			receiver.removeTemp( "BODY_CHANGE_POS" )
		return Buff_Normal.doLoop( self, receiver, buffData ) and self.isEnd != True

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

		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		self = buffData[ "skill" ]
		if receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and receiver.isRideOwner: # 如果镖车上有人，强制人下镖车
			receiver.disMountEntity( receiver.ownerID, receiver.ownerID )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if receiver.vehicle and receiver.vehicle.isSlaveDart(): # 如果人在镖车上，强制人下镖车
				receiver.vehicle.disMountEntity( receiver.id, receiver.id )
			if getCurrVehicleID( receiver ): # 如果人在骑宠上，强制下骑宠
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.begin_body_changing( self._p1, self._p2 )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.planesAllClients( "onSetModelScaleTime", (0.0, ) ) #不需要缩放时间
			receiver.modelScale = self._p2

		receiver.appendAttackerHit(buffData[ "skill" ])
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		

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
		Buff_Normal.doReload( self, receiver, buffData )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and receiver.isRideOwner: # 如果镖车上有人，强制人下镖车
			receiver.disMountEntity( receiver.ownerID, receiver.ownerID )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if receiver.vehicle and receiver.vehicle.isSlaveDart(): # 如果人在镖车上，强制人下镖车
				receiver.vehicle.disMountEntity( receiver.id, receiver.id )
			if getCurrVehicleID( receiver ): # 如果人在骑宠上，强制下骑宠
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.begin_body_changing( self._p1, self._p2 )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.planesAllClients( "onSetModelScaleTime", (0.0,) ) #不需要缩放时间
			receiver.modelScale = self._p2

		receiver.appendAttackerHit(buffData[ "skill" ])
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		

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
		if receiver.isMoving(): # 如果BUFF结束时对象还在随机走动，则将其停止
			receiver.stopMoving()
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTemp( "ROLE_BODY_BUFF_END", True )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.end_body_changing( receiver.id, "" )
			receiver.setTemp( "ROLE_BODY_BUFF_END", False )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			receiver.modelNumber = self.currModelNumber
			receiver.planesAllClients( "onSetModelScaleTime", (0.0,) ) #不需要缩放时间
			receiver.modelScale = self.currModelScale

		receiver.removeAttackerHit( buffData[ "skill" ].getUID() )
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		
		receiver.removeTemp( "BODY_CHANGE_POS" )
	
	def springOnDamage( self, caster, skill ):
		"""
		接收伤害后
		"""
		self.isEnd = True

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "isEnd" : self.isEnd, "currModelNumber" : self.currModelNumber, "currModelScale" : self.currModelScale } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_108006()
		obj.__dict__.update( self.__dict__ )
		obj.isEnd = data["param"]["isEnd"]
		self.currModelNumber = data["param"]["currModelNumber"]
		self.currModelScale = data["param"]["currModelScale"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
#
# 
#