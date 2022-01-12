# -*- coding: gb18030 -*-
#
# $Id: QuestMonster.py,v 1.2 2007-06-14 09:58:00 huangyongwei Exp $

"""
怪物NPC的类
"""

import Monster
import Language
from bwdebug import *
import random

class QuestMonster(Monster.Monster):
	"""
	怪物NPC类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.Monster.__init__( self )
		self._RequireQuest = []

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		Monster.Monster.load( self, section )
		self._RequireQuest = section["RequireQuest"].readInts( "quest" )

	def checkDamageValid( self, caster ):
		"""
		如果没有完成 任务则不会受击
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
# 任务怪物
#
#