# -*- coding:gb18030 -*-

from bwdebug import *
import csdefine
import csconst
import event.EventCenter as ECenter
import BigWorld
from Sound import soundMgr


class RoleEidolonHandler:
	"""
	玩家小精灵操作接口
	"""
	def __init__( self ):
		"""
		"""
		pass

	def conjureEidolon( self ):
		"""
		召唤小精灵
		"""
		self.cell.conjureEidolon()

	def withdrawEidolon( self ) :
		"""
		收回小精灵
		"""
		self.cell.withdrawEidolon()

	def vipShareSwitch( self ) :
		"""
		小精灵VIP功能共享
		"""
		self.cell.vipShareSwitch()

	def eidolonDirect( self, objectID ):
		"""
		精灵指引
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_SHOW_COURSE_HELP" )

	def eidolonQueryHelp( self, objectID ):
		"""
		指引查询
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", "" )

	def eidolonLevelHelp( self, objectID ):
		"""
		等级帮助
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_TOGGLE_HELP_WINDOW" )

	def set_vip( self, oldValue ):
		"""
		"""
		pass

	def onEidolonLeaveWorld( self ) :
		"""
		玩家的小精灵消失时通知主人（非定义方法）
		"""
		pass
		
	def onWithdrawEidolon( self ) :
		"""
		收回小精灵，播放语音
		"""
		soundMgr.play2DSound( "xitongyuyin/xt_xiaojingling01" )
