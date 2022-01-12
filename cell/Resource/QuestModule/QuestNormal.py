# -*- coding: gb18030 -*-
# add by huangliang 2012-4-10

"""
普通任务类型1
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
		self._style = csdefine.QUEST_STYLE_NORMAL1		# 新类型与Normal类型基本一致，唯一区别是等级差超过10级，依然会显示绿色感叹号的接取任务提示。