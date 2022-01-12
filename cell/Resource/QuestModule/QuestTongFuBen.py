# -*- coding: gb18030 -*-

import Love3
import time
from Quest import Quest
import csdefine

TONG_NORMAL_SPELL = 122152003

class QuestTongFuBen(Quest):
	def __init__(self):
		Quest.__init__(self)
		self.repeatable_ = 1		# 帮会副本子任务必须可重复，不然如果接到已经完成过的子任务，会出现不能提交的问题。-- modify by cwl
	
	def init( self, section ):
		self._type = csdefine.QUEST_STYLE_TONG_FUBEN
		Quest.init(self, section)
	
	def onComplete( self, player ):
		player.addActivityCount( csdefine.ACTIVITY_TONG_FUBEN )
		Quest.onComplete(self, player)
	
	def abandoned( self, player, flags ):
		Love3.g_skills[TONG_NORMAL_SPELL].receiveLinkBuff( player, player ) #添加自省BUFF
		return Quest.abandoned(self, player, player)
	