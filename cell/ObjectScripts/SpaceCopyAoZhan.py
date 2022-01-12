# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csconst
import csstatus
import Const

class SpaceCopyAoZhan( SpaceCopy ):
	# 鏖战群雄
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		SpaceCopy.initEntity( self, selfEntity )
	
	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainShenGuiMiJing时，传递参数
		"""
		d = {}
		d[ "playerDBID" ] = entity.databaseID
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		d = {}
		d[ "roleName" ] = entity.getName()
		d.update( SpaceCopy.packedSpaceDataOnEnter( self, entity ) )
		return d
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		进入
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		startTime = selfEntity.params[ "roundTime" ] + 60 - time.time()#准备时间是60秒
		if startTime:
			if startTime > 60:
				startTime = 60
			baseMailbox.client.aoZhan_countDown( int( startTime ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		离开
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		killerType = 0
		killerBase = None
		if killer:
			killerType = killer.getEntityType()
			if killerType == csdefine.ENTITY_TYPE_PET:
				petOwner = killer.getOwner()
				if petOwner.etype == "MAILBOX":
					killerBase = petOwner.entity.base
			else:
				killerBase  = killer.base
		
		role.getCurrentSpaceBase().cell.onRoleBeKill( role.base, killerBase )
	
	def activityStart( self, selfEntity ):
		selfEntity.battleData.setPkMode()
	
	def kickAllPlayer( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoEnterPos()
			else:
				e.cell.gotoEnterPos()
	
	def closeActivity( self, selfEntity ):
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_IS_CLOSE, "" )
			else:
				e.cell.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_IS_CLOSE, "" )
				
		selfEntity.addTimer( 15.0, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( 20.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		selfEntity.battleData.resertPkMode()
		
	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		SpaceCopy.onTimer( self, selfEntity, id, userArg )