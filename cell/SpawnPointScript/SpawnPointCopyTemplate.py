# -*- coding: gb18030 -*-

"""
�����й�����������ͣ���������������Ҫֱ�Ӵ������������������Ҫ����
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPointCopy import SpawnPointCopy

class SpawnPointCopyTemplate( SpawnPointCopy ):
	"""
	�¸���ģ��ʹ�õĹ������������,�������¸���ģ�� CopyTemplate �������ࡣ
	����
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		try :
			selfEntity.getCurrentSpaceBase().copyTemplate_addSpawnPoint( selfEntity.base, selfEntity.queryTemp( "monsterType", 0 ) )
		except :
			ERROR_MSG( "this SpawnPoint only use new copy 'CopyTemplate' or it's subclass." )

