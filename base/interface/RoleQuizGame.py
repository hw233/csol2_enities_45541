# -*- coding: gb18030 -*-
#

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csconst
import csdefine
from bwdebug import *
import sys

class RoleQuizGame:
	"""
	玩家知识问答模块
	"""
	def __init__( self ):
		"""
		"""
		pass

	def isQuizGaming( self ):
		"""
		活动是否开始
		"""
		return BigWorld.globalData.has_key( "QuizGame_start" )

	def quiz_useGold( self, questionID, scoreRate ):
		"""
		Define method.
		使用元宝答题

		@param questionID : 题目id
		@param questionID : UINT16
		@param scoreRate : 得分倍率，如果使用幸运星答对会得双倍积分。
		@type scoreRate : UINT8
		"""
		if self.payGold( csconst.QUIZ_GOLD_CONSUME, csdefine.CHANGE_GOLD_QUIZ_USEGOLD ):
			INFO_MSG( "--->>>玩家( %s )使用元宝( %i )答题。" % ( self.getName(), csconst.QUIZ_GOLD_CONSUME ) )

			self.getQuizGameMgr().useYourHead( self.databaseID, questionID, scoreRate )
		else:
			self.statusMessage( csstatus.GOLD_NO_ENOUGH )

	def getQuizGameMgr( self ):
		"""
		获得知识问答管理器
		"""
		return BigWorld.globalData[ "QuizGameMgr" ]
