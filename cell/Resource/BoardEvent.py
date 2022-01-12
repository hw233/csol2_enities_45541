# -*- coding: gb18030 -*-

import csdefine
import csstatus
from bwdebug import *
from Love3 import g_skills

class BoardEvent:
	"""
	�����¼�
	"""
	def __init__( self ):
		self._id = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		self.id = section["id"].asInt
		self.describe = section["describe"].asString
		self.type = csdefine.CHESS_BOARD_EVE_NONE

	def getID( self ):
		"""
		��ȡ�¼�ID
		"""
		return self.id

	def do( self, player ):
		"""
		�����¼�
		"""
		player.statusMessage( csstatus.DESTINY_TRANS_ONLY_FOR_NOTICE, self.describe )
		INFO_MSG( " Role %s has triggled event %i, describe %s " % ( player.getNameAndID(), self.id, self.describe ))

	def triggerExtraEffect( self, player ):
		"""
		��������Ч��
		"""
		pass

	def endExtraEffect( self, player ):
		"""
		��������Ч��
		"""
		pass

class BoardEventStart( BoardEvent ):
	"""
	���
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
	����ǰ�����ߺ���
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
	���Buff
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
		��������Ч��
		"""
		skill = g_skills[ self.skillID ]
		skill.receiveLinkBuff( player, player )

	def endExtraEffect( self, player ):
		"""
		��������Ч��
		"""
		player.removeBuffByID( self.buffID,  [csdefine.BUFF_INTERRUPT_NONE] )

class BoardEventMultDrop( BoardEvent ):
	"""
	�౶����
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
		��������Ч��
		"""
		player.setTemp( "MULT_DROP", self.multDrop )

	def endExtraEffect( self, player ):
		"""
		��������Ч��
		"""
		player.removeTemp( "MULT_DROP" )

class BoardEventBoss( BoardEvent ):
	"""
	ˢBoss
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
		��������Ч��
		"""
		pass

	def endExtraEffect( self, player ):
		"""
		��������Ч��
		"""
		pass

class BoardEventEnd( BoardEvent ):
	"""
	����
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