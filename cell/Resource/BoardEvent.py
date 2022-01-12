# -*- coding: gb18030 -*-

import csdefine
import csstatus
from bwdebug import *
from Love3 import g_skills

class BoardEvent:
	"""
	棋盘事件
	"""
	def __init__( self ):
		self._id = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		self.id = section["id"].asInt
		self.describe = section["describe"].asString
		self.type = csdefine.CHESS_BOARD_EVE_NONE

	def getID( self ):
		"""
		获取事件ID
		"""
		return self.id

	def do( self, player ):
		"""
		触发事件
		"""
		player.statusMessage( csstatus.DESTINY_TRANS_ONLY_FOR_NOTICE, self.describe )
		INFO_MSG( " Role %s has triggled event %i, describe %s " % ( player.getNameAndID(), self.id, self.describe ))

	def triggerExtraEffect( self, player ):
		"""
		触发额外效果
		"""
		pass

	def endExtraEffect( self, player ):
		"""
		结束额外效果
		"""
		pass

class BoardEventStart( BoardEvent ):
	"""
	起点
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )

	def do( self, player ):
		"""
		"""
		pass

class BoardEventMove( BoardEvent ):
	"""
	棋子前进或者后退
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )
		self.point = section.readInt( "param1" )
		self.type = csdefine.CHESS_BOARD_EVE_MOVE

	def do( self, player ):
		"""
		"""
		BoardEvent.do( self, player )
		player.moveChess( self.point )

class BoardEventBuff( BoardEvent ):
	"""
	添加Buff
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )
		self.skillID = section.readInt( "param1" )
		self.buffID = int( section.readString( "param2") )
		self.type = csdefine.CHESS_BOARD_EVE_BUFF

	def do( self, player ):
		"""
		"""
		BoardEvent.do( self, player )
		player.enterDestinyTransGate( self.type, self.id )

	def triggerExtraEffect( self, player ):
		"""
		触发额外效果
		"""
		skill = g_skills[ self.skillID ]
		skill.receiveLinkBuff( player, player )

	def endExtraEffect( self, player ):
		"""
		结束额外效果
		"""
		player.removeBuffByID( self.buffID,  [csdefine.BUFF_INTERRUPT_NONE] )

class BoardEventMultDrop( BoardEvent ):
	"""
	多倍掉落
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )
		self.type = csdefine.CHESS_BOARD_EVE_DROP
		self.multDrop = section.readInt( "param1" )

	def do( self, player ):
		"""
		"""
		BoardEvent.do( self, player )
		player.enterDestinyTransGate( self.type, self.id )

	def triggerExtraEffect( self, player ):
		"""
		触发额外效果
		"""
		player.setTemp( "MULT_DROP", self.multDrop )

	def endExtraEffect( self, player ):
		"""
		结束额外效果
		"""
		player.removeTemp( "MULT_DROP" )

class BoardEventBoss( BoardEvent ):
	"""
	刷Boss
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )
		self.type = csdefine.CHESS_BOARD_EVE_BOSS

	def do( self, player ):
		"""
		"""
		BoardEvent.do( self, player )
		player.enterDestinyTransGate( self.type, self.id )

	def triggerExtraEffect( self, player ):
		"""
		触发额外效果
		"""
		pass

	def endExtraEffect( self, player ):
		"""
		结束额外效果
		"""
		pass

class BoardEventEnd( BoardEvent ):
	"""
	结束
	"""
	def __init__( self ):
		"""
		"""
		BoardEvent.__init__( self )

	def init( self, section ):
		"""
		"""
		BoardEvent.init( self, section )

	def do( self, player ):
		"""
		"""
		BoardEvent.do( self, player )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].onRolePassedAllGate( player.base, player.databaseID, player.teamMailbox.id )