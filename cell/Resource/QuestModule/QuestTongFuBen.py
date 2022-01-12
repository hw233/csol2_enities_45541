# -*- coding: gb18030 -*-

import Love3
import time
from Quest import Quest
import csdefine

TONG_NORMAL_SPELL = 122152003

class QuestTongFuBen(Quest):
	def __init__(self):
		Quest.__init__(self)
		self.repeatable_ = 1		# ��ḱ�������������ظ�����Ȼ����ӵ��Ѿ���ɹ��������񣬻���ֲ����ύ�����⡣-- modify by cwl
	
	def init( self, section ):
		self._type = csdefine.QUEST_STYLE_TONG_FUBEN
		Quest.init(self, section)
	
	def onComplete( self, player ):
		player.addActivityCount( csdefine.ACTIVITY_TONG_FUBEN )
		Quest.onComplete(self, player)
	
	def abandoned( self, player, flags ):
		Love3.g_skills[TONG_NORMAL_SPELL].receiveLinkBuff( player, player ) #�����ʡBUFF
		return Quest.abandoned(self, player, player)
	