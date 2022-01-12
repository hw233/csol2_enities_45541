# -*- coding: gb18030 -*-

# 星际地图
# by daiqinghui

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
import Const
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#玩家全部离开副本后，隔多久副本才删除
LEAVE_SPACECOPY_STAR_MAP			 = 100001


class SpaceCopyStarMap( SpaceCopy ) :
	"""
	星际地图管理器
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.initAccumPoint() 				# 玩家进入星际地图，给予一定的气运
			skills = {}
			if self.className in player.mapSkills:
				skills = player.mapSkills[self.className]
			player.client.showPGControlPanel( skills )
			INFO_MSG( "%s enter copy space star." % player.getName() )
		else :
			INFO_MSG( "Something enter copy space star." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.resetAccumPoint()							# 玩家离开星际地图，气运值置0
			player.removeTemp("callPGDict")							# 将召唤列表清空
			player.removeTemp("pg_formation")
			player.client.closePGControlPanel()
			INFO_MSG( "%s leave copy space star." % player.getName() )
		else :
			INFO_MSG( "Something leave copy space star." )
			
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def infoSpaceCopyStar( self, leaveTime ):
		"""
		"""
		self.addTimer( leaveTime, 0, LEAVE_SPACECOPY_STAR_MAP )
		self.addTimer( 60, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == LEAVE_SPACECOPY_STAR_MAP:
			if len( self._players ) == 0:
				INFO_MSG( "all players have leaved SpaceCopy." )
				return
			for e in self._players:
				BigWorld.entities[e.id].gotoForetime()
				
		if userArg == Const.SPACE_COPY_CLOSE_CBID:
			if len( self._players ) != 0:
				INFO_MSG( "someOne in SpaceCopy, cannot close spece." )
				return
			self.base.closeSpace( True )
			return
