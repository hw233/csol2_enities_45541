# -*- coding: gb18030 -*-
# add by huangliang 2012-4-10

"""
��ͨ��������1
"""

import csdefine
import csstatus
from Quest import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
import random
from string import Template
import QTReward
import QTTask


class QuestNormal( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		
	def init( self, section ):
		"""
		"""
		Quest.init( self, section )
		self._style = csdefine.QUEST_STYLE_NORMAL1		# ��������Normal���ͻ���һ�£�Ψһ�����ǵȼ����10������Ȼ����ʾ��ɫ��̾�ŵĽ�ȡ������ʾ��