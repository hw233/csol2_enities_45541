# -*- coding: gb18030 -*-
# ����������Entity 2009-01-19 SongPeifang & LinQing
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine

class SpecialHideEntity( NPCObject ):
	"""
	����������Entity��
	������Ŀ�ģ�������ҵ����á�
	��ҵ���ʱ����Ҫ֪���Ƿ������ں��ߵ�������ר�Ź��������������Entity
	���Entity��Ҫ�ɲ߻�����Ĳ���һ���ں���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )