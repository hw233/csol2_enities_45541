# -*- coding: gb18030 -*-

import csdefine
from Quest import *

class QuestAuto( Quest ):
	# �Զ�����ר������
	def __init__( self ):
		"""
		"""
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_AUTO