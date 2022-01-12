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
	���֪ʶ�ʴ�ģ��
	"""
	def __init__( self ):
		"""
		"""
		pass

	def isQuizGaming( self ):
		"""
		��Ƿ�ʼ
		"""
		return BigWorld.globalData.has_key( "QuizGame_start" )

	def quiz_useGold( self, questionID, scoreRate ):
		"""
		Define method.
		ʹ��Ԫ������

		@param questionID : ��Ŀid
		@param questionID : UINT16
		@param scoreRate : �÷ֱ��ʣ����ʹ�������Ǵ�Ի��˫�����֡�
		@type scoreRate : UINT8
		"""
		if self.payGold( csconst.QUIZ_GOLD_CONSUME, csdefine.CHANGE_GOLD_QUIZ_USEGOLD ):
			INFO_MSG( "--->>>���( %s )ʹ��Ԫ��( %i )���⡣" % ( self.getName(), csconst.QUIZ_GOLD_CONSUME ) )

			self.getQuizGameMgr().useYourHead( self.databaseID, questionID, scoreRate )
		else:
			self.statusMessage( csstatus.GOLD_NO_ENOUGH )

	def getQuizGameMgr( self ):
		"""
		���֪ʶ�ʴ������
		"""
		return BigWorld.globalData[ "QuizGameMgr" ]
