# -*- coding: gb18030 -*-
#
# $Id: QuestMonster.py,v 1.2 2007-06-14 09:58:00 huangyongwei Exp $

"""
����NPC����
"""

import Monster
import Language
from bwdebug import *
import random

class QuestMonster(Monster.Monster):
	"""
	����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.Monster.__init__( self )
		self._RequireQuest = []

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		Monster.Monster.load( self, section )
		self._RequireQuest = section["RequireQuest"].readInts( "quest" )

	def checkDamageValid( self, caster ):
		"""
		���û����� �����򲻻��ܻ�
		"""
		for qid in self._RequireQuest:
			if not caster.questIsCompleted( qid ):
				return False
		return True


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/04/11 02:04:47  phw
# no message
#
# Revision 1.1  2007/03/23 05:47:19  kebiao
# �������
#
#