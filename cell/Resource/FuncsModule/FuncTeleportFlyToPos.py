# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import BigWorld
import csstatus
import csdefine
import Const
import re
import VehicleHelper
import ECBExtend
import utils

class FuncTeleportFlyToPos( Function ):
	"""
	传送 飞到指定位置
	"""
	def __init__( self, section ):
		"""
		param1: spaceName
		param2: x, y, z
		param3: d1, d2, d3
		param4: radius

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.patrolPathNode = section.readString( "param1" )
		self.patrolList = section.readString( "param2" )
		# 提供给buff用于上线后直接传送到目的地
		self.spaceName = section.readString( "param3" )
		
		self.pos = None
		position = section.readString( "param4" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos
		
		self.direction = ( 0, 0, 0 )
		param5 = section.readString( "param5" ).split(";")
		self.skillID = 0
		self.isCheckVehicle = 1 #释放技能是否检测坐骑
		if len(param5) == 1:
			self.skillID = int( param5[0] )
		elif len(param5) == 2:
			self.skillID = int( param5[0] )
			self.isCheckVehicle = int( param5[1] )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
		isFlag = False #下坐骑标志
		if self.isCheckVehicle:
			if player.vehicle or VehicleHelper.getCurrVehicleID( player ):
				player.statusMessage( csstatus.VEHICLE_TELEPORT_FAILED )
				return
		else:
			if VehicleHelper.getCurrVehicleID( player ): # 如果人在骑宠上，强制下骑宠
				player.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
				isFlag = True
		# 如果有法术禁咒buff
		if len( player.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return

		# 如果在吟唱则中断吟唱
		if player.attrIntonateSkill or\
			( player.attrHomingSpell and player.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			player.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )

		# 记录要到达的地方
		player.setTemp( "teleportFly_data", ( self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction ) )
		if isFlag:
			talkEntity.setTemp( "talkfuncskill", ( self.skillID, player.id ) )
			talkEntity.addTimer( 0.5, 0.0, ECBExtend.FUNCTION_SPELL_TIMER_CBID )
		else:
			talkEntity.spellTarget( self.skillID, player.id )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True



