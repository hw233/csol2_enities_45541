# -*- coding: gb18030 -*-
#
# �չ�ԡ��̲���ǳ������ 2009-01-16 SongPeifang
#

import BigWorld
from bwdebug import *
from QuestBox import QuestBox

class QuestShellBox( QuestBox ):
	"""
	QuestShellBox��
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		QuestBox.__init__( self )
	
	def spawnShell( self ):
		"""
		��cell�������ˢ��
		"""
		if hasattr( self, "cell" ):	# �ж�һ��cell�Ƿ��Ѿ�������
			self.cell.spawnShell()