# -*- coding: gb18030 -*-
#
"""
持续性效果
"""

import BigWorld
import random
import Math
from Buff_Normal import Buff_Normal
import csdefine
import csstatus
from Function import newUID
import Const

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_108009( Buff_Normal ):
	"""
	example:逃窜
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.moveRadius = 0.0
		self.moveSpeed = 0.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 1.0
		self.moveRadius = float( dict["Param1"] if len( dict["Param1"] ) > 0 else 0 )	# 逃窜半径
		self.moveSpeed = float( dict["Param2"] if len( dict["Param2"] ) > 0 else 0 )	# 逃窜速度
		
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

		# 打断施法
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ):
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )

		# 执行附加效果
		receiver.move_speed = self.moveSpeed
		receiver.updateTopSpeed()
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )

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
		centerPos = Math.Vector3( receiver.position )
		receiver.doRandomRun( centerPos, self.moveRadius )
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
		Buff_Normal.doReload( self, receiver, buffData )

		# 执行附加效果
		receiver.move_speed = self.moveSpeed
		receiver.updateTopSpeed()
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
		if receiver.isMoving():		# 停止移动
			receiver.stopMoving()

		# 移除附加效果
		receiver.calcMoveSpeed()
		receiver.updateTopSpeed()
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : { "moveRadius": self.moveRadius, "moveSpeed": self.moveSpeed } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_108009()
		obj.__dict__.update( self.__dict__ )
		obj.moveRadius = data["param"]["moveRadius"]
		obj.moveSpeed = data["param"]["moveSpeed"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj