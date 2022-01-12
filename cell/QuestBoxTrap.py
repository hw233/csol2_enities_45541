# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.6 2008-01-08 06:25:59 yangkai Exp $

from QuestBox import QuestBox

import BigWorld
from bwdebug import *

class QuestBoxTrap( QuestBox ) :
	"""
	用于查探类型任务
	"""
	def __init__( self ) :
		QuestBox.__init__( self )

	def taskStatus( self, srcEntityID ):
		"""
		Exposed method.
		通过这个方法来确定玩家已经到达了这个区域
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return
		
		scriptObject = self.getScript()
#		quest = playerEntity.getQuest( questID )
		for questID, taskIndex in scriptObject.questData.iteritems():
			if playerEntity.has_quest( questID ):
				task = playerEntity.getQuestTasks( questID ).getTasks()[taskIndex]
				if not task.isCompleted( playerEntity ):
					playerEntity.questTaskIncreaseState( questID, taskIndex )
