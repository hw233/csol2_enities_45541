# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPrison.py,v 1.2 2008-08-28 00:52:47 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import random
import time
import Const
from bwdebug import *
from SpaceMultiLine import SpaceMultiLine
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyPrison( SpaceMultiLine ):
	"""
	监狱
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceMultiLine.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceMultiLine.load( self, section )
		data = section[ "Space" ][ "NPCPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )

		self.funcNPCData = ( section[ "Space" ][ "NPCClassID" ].asString, pos, direction )

		self.guards = []
		datas = section[ "Space" ][ "GuardData" ]
		for data in datas.values():
			pos 	  = tuple( [ float(x) for x in data[ "position" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.guards.append( ( data[ "NPCClassID" ].asString, pos, direction ) )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		# 刷功能NPC
		selfEntity.createNPCObject( self.funcNPCData[0], self.funcNPCData[1], self.funcNPCData[2], { "tempMapping" : {} } )

		# 刷守卫
		for item in self.guards:
			params = { "spawnPos" : item[1], "tempMapping" : {} }
			selfEntity.createNPCObject( item[0], item[1], item[2], params )

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		# 只有系统抓捕的时候才会设置这个标记， 任何其他途径都无法进入
		if not entity.popTemp( "gotoPrison", False ):
			return csstatus.SPACE_MISS_ENTER_PRISON
		return csstatus.SPACE_OK

	def checkDomainLeaveEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		# 只有系统抓捕的时候才会设置这个标记， 任何其他途径都无法进入
		if not entity.popTemp( "leavePrison", False ):
			return csstatus.SPACE_MISS_LEAVE_PRISON
		return csstatus.SPACE_OK

	def packedMultiLineDomainData( self, entity ):
		"""
		virtual method.
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		return {}

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		return SpaceMultiLine.packedSpaceDataOnEnter( self, entity )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		pass

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceMultiLine.onEnter( self, selfEntity, baseMailbox, params )
		DEBUG_MSG( "%i enter prison params=%s" % ( baseMailbox.id, params ) )
		entity = BigWorld.entities.get( baseMailbox.id )
		entity.endPkValueTimer()
		entity.startPkValueTimer( Const.PK_VALUE_PRISON_LESS_TIME, Const.PK_VALUE_PRISON_LESS_TIME )

		# 入狱后相应频道禁言
		prison_cant_channels = [
			csdefine.CHAT_CHANNEL_TEAM,						# 队伍
			csdefine.CHAT_CHANNEL_TONG,						# 帮会
			csdefine.CHAT_CHANNEL_WORLD,					# 世界
			]
		entity.base.chat_lockMyChannels( prison_cant_channels, csdefine.CHAT_FORBID_JAIL, 0 )

		# 如果角色已经死亡就先复活他再判个终身监禁（丫的就是不送便宜） by 姜毅
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			entity.reviveOnOrigin()

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceMultiLine.onLeave( self, selfEntity, baseMailbox, params )
		DEBUG_MSG( "%i leave prison params=%s" % ( baseMailbox.id, params ) )
		entity = BigWorld.entities.get( baseMailbox.id )
		entity.endPkValueTimer()
		if len( entity.findBuffsByBuffID( 99018 ) ) == 0 and entity.pkValue > 0:
			entity.startPkValueTimer()

		# 出狱后解除相应频道的禁言
		prison_cant_channels = [
			csdefine.CHAT_CHANNEL_TEAM,						# 队伍
			csdefine.CHAT_CHANNEL_TONG,						# 帮会
			csdefine.CHAT_CHANNEL_WORLD,					# 世界
			]
		entity.base.chat_unlockMyChannels( prison_cant_channels, csdefine.CHAT_FORBID_JAIL )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass


