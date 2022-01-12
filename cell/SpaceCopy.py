# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2008-01-28 06:08:59 kebiao Exp $

"""
"""
import time
import BigWorld
import csdefine
import csconst
from bwdebug import *
from SpaceNormal import SpaceNormal
import Const
import csstatus

class SpaceCopy( SpaceNormal ):
	"""
	副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceNormal.__init__( self )
		BigWorld.cellAppData[ self.getSpaceGlobalKey() ] = self.base

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		self.getScript().onEnter( self, baseMailbox, params )
		if self.getScript().isViewer( params ):
			self.onEnterViewer( baseMailbox, params)
		else:
			self.onEnterCommon( baseMailbox, params )
	
	def onEnterViewer( self, baseMailbox, params ):
		# 以观察者的身份进入副本
		self.getScript().onEnterViewer( self, baseMailbox, params )
		baseMailbox.cell.spaceViewerEnterState()
		self.spaceViewers.append( baseMailbox )
	
	def onEnterCommon( self, baseMailbox, params ):
		# 以正常的方式进入副本
		self.getScript().onEnterCommon( self, baseMailbox, params )
		self.registerPlayer( baseMailbox, params )
		# 锁定PK模式,并标记（用于离开安全区是否解锁PK模式的判断）
		baseMailbox.cell.lockPkMode()
		baseMailbox.cell.setTemp( "copy_space_lock_pkmode", 1 )
		#进入副本通知改变战斗关系模式
		if self.getScript().getSpaceType() in csconst.SPACE_MAPPING_RELATION_TYPE_DICT:
			baseMailbox.cell.changeRelationMode( csconst.SPACE_MAPPING_RELATION_TYPE_DICT[ self.getScript().getSpaceType() ] )
		# 通知base，记录当前有多少个玩家进入了space，以判断当前space是否满员
		self.base.onEnter( baseMailbox, params )
		# 调用底层接口
		SpaceNormal.onEnter( self, baseMailbox, params )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		if self.getScript().isViewer( params ):
			self.onLeaveViewer( baseMailbox, params)
		else:
			self.onLeaveCommon( baseMailbox, params )

	def onLeaveViewer( self, baseMailbox, params ):
		# 以观察者的身份退出副本
		self.getScript().onLeaveViewer( self, baseMailbox, params )
		baseMailbox.cell.spaceViewerLeaveState()
		for index, mailbox in enumerate( self.spaceViewers ):
			if mailbox.id == baseMailbox.id:
				self.spaceViewers.pop( index )
				break
	
	def onLeaveCommon( self, baseMailbox, params ):
		# 以正常的方式退出副本
		self.getScript().onLeaveCommon( self, baseMailbox, params )
		self.unregisterPlayer( baseMailbox, params )
		# 解锁PK模式
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.removeTemp( "copy_space_lock_pkmode" )
		#离开副本通知战斗关系模式改变
		if self.getScript().getSpaceType() in csconst.SPACE_MAPPING_RELATION_TYPE_DICT:
			baseMailbox.cell.changeRelationMode( csdefine.RELATION_STATIC_CAMP )
		# 通知base，记录当前有多少个玩家进入了space，以判断当前space是否满员
		self.base.onLeave( baseMailbox, params )
		# 调用底层接口
		baseMailbox.client.onCloseCopySpaceInterface()
		SpaceNormal.onLeave( self, baseMailbox, params )
		
	def registerPlayer( self, baseMailbox, params = {} ): # 对于帮会领地这种公共空间，但是又有N多活动的对象，多保存一点信息有助于对不同活动进行编程，所以增加一个默认参数params by mushuang
		"""
		注册进入此space的mailbox和玩家名称
		"""
		for pMB in self._players:
			if pMB.id == baseMailbox.id:
				ERROR_MSG( "player(%i) repeat register on space.spaceName: %s, spaceID: %s."%( baseMailbox.id, self.className, self.spaceID ) )
				return
		self._players.append( baseMailbox )
		BigWorld.globalData[ "SpaceViewerMgr" ].playerEnterSpaceCopy( self.className, self.spaceID, time.time(), baseMailbox )
		
	def unregisterPlayer( self, baseMailbox, params = {} ):
		"""
		取消该玩家的记录
		"""
		BigWorld.globalData[ "SpaceViewerMgr" ].playerLeaveSpaceCopy( self.className, self.spaceID, baseMailbox )
		for i, pMB in enumerate( self._players ):
			if pMB.id == baseMailbox.id:
				self._players.pop( i )
				return
		ERROR_MSG( "unregister player(%i) fail,spaceName: %s."%( baseMailbox.id, self.className ) )
	
	def onAINotifySpaceCreated( self, className, entity ):
		"""
		define method.
		AI通知NPC创建
		"""
		for i, mb in enumerate( self.aiRecordMonster ):
			if mb.id == entity.id:
				ERROR_MSG( "monster(%i) repeat register on space.spaceName: %s, spaceID: %s."%( entity.id, self.className, self.spaceID ) )
				return
				
		self.aiRecordMonster.append( entity )

	def onAINotifySpaceDied( self, className, entity ):
		"""
		define method.
		AI通知NPC死亡
		"""
		for i, mb in enumerate( self.aiRecordMonster ):
			if mb.id == entity.id:
				self.aiRecordMonster.pop( i )
				return
				
		ERROR_MSG( "unregister monster(%i) fail,spaceName: %s."%( entity.id, self.className ) )
		
	def onConditionChange( self, params ):
		"""
		define method
		用于副本的事件变化通知。
		副本的事件变化可以是多个变化构成一个内容的完成，也可以是一个。
		"""
		self.getScript().onConditionChange( self, params )


	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		此接口用于通知角色加载地图完毕，可以移动了，可以正常和其他游戏内容交流。
		@param baseMailbox: 要离开此space的entity mailbox
		"""
		SpaceNormal.onTeleportReady( self, baseMailbox )
		baseMailbox.client.onOpenCopySpaceInterface( self.shownDetails() )
		
	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
		]
		"""
		# 默认显示的三项，其余有显示的需要，需要在另外定义shownDetails
		return [ 0, 1, 3 ]
	
	def onDestroy( self ):
		"""
		cell 被删除时发生
		"""
		gbKey = self.getSpaceGlobalKey()
		if BigWorld.cellAppData.has_key( gbKey ):
			del BigWorld.cellAppData[ gbKey ]
			
		SpaceNormal.onDestroy( self )

	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		if userArg == Const.SPACE_COPY_CLOSE_CBID:
			self.base.closeSpace( True )
			return
		SpaceNormal.onTimer( self, id, userArg )
	
		
	def getSpaceGlobalKey( self ):
		"""
		获取队伍进入global key
		"""
		spaceType = self.getScript().getSpaceType()
		teamId = self.params['teamID'] if self.params.has_key( "teamID" ) else 0
		difficulty = self.params[ "difficulty" ] if self.params.has_key( "difficulty" ) else 0
		if Const.SPACE_COPY_GLOBAL_KEY.has_key( spaceType ):
			return Const.GET_SPACE_COPY_GLOBAL_KEY( spaceType, teamId, difficulty )
		else:
			return ""
	
	def nofityTeamDestroy( self, teamEntityID ):
		"""
		define method
		通知副本某队伍解散
		"""
		self.getScript().nofityTeamDestroy( self, teamEntityID )
	
	def getPlayerNumber( self ):
		return len( self._players )
	
	def checkSpaceIsFull( self ):
		"""
		检查空间是否满员
		"""
		return False
	
	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		有玩家请求进入副本
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			playerMB.cell.onSpaceCopyTeleport( actType, self.className, pos, direction, not( playerDBID in self._enterRecord ) )