# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import csconst
import csstatus
import csdefine
import Const
from Buff_Normal import Buff_Normal


class Buff_99008( Buff_Normal ):
	"""
	跟随buff，同步与队长的速度，检测是否还满足跟随条件
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

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
		if receiver.isTeamCaptain():
			return

		followEntity = receiver.getTeamCaptain()
		if followEntity is None:
			receiver.cancelTeamFollow()
			return

		if followEntity.vehicle is not None:
			followEntity = followEntity.vehicle

		moveEntity = receiver
		if receiver.vehicle:
			moveEntity = receiver.vehicle

		if moveEntity.move_speed != followEntity.move_speed:
			moveEntity.setMoveSpeed( followEntity.move_speed )
		#DEBUG_MSG( "-------->>>moveEntity( %i ),speed( %f )" % ( moveEntity.id, moveEntity.move_speed ) )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果循环的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		if receiver.isTeamCaptain():
			return True

		followEntity = receiver.getTeamCaptain()
		if followEntity is None:
			#DEBUG_MSG( "------->>>receiver( %s )followEntity is None" % receiver.getName() )
			return False

		if receiver.position.distTo( followEntity.position ) > csconst.TEAM_FOLLOW_DISTANCE:	# 检查是否符合跟随条件
			#DEBUG_MSG( "------->>>receiver( %s ) position > 20,,cancel....,()" % receiver.getName() )
			return False

		if followEntity.vehicle is not None:
			followEntity = followEntity.vehicle

		moveEntity = receiver
		if moveEntity.vehicle is not None:
			moveEntity = moveEntity.vehicle

		if moveEntity.move_speed != followEntity.move_speed:
			moveEntity.setMoveSpeed( followEntity.move_speed )
		#DEBUG_MSG( "-------->>>wsf---moveEntity( %i ),speed( %f )" % ( moveEntity.id, moveEntity.move_speed ) )
		return True

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		if receiver.isTeamCaptain():
			return

		if receiver.vehicle is not None:
			receiver.vehicle.calcMoveSpeed()
			return

		receiver.calcMoveSpeed()
		#DEBUG_MSG( "-------->>>moveEntity( %i ),speed( %f )" % ( moveEntity.id, moveEntity.move_speed ) )
