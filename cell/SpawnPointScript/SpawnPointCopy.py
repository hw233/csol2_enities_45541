# -*- coding: gb18030 -*-

"""
�����й�����������ͣ���������������Ҫֱ�Ӵ������������������Ҫ����
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointCopy( SpawnPoint ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )

	def onBaseGotCell( self, selfEntity ):
		"""
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		# ��base�����onGetCell()�ص����ٿ�ʼ������������������ܽ���������ʱ�����㲻��ȷ������
		# ��ǰ������ܿ����ǵײ��bug
		pass	# ������������㣬����Ҫ����������Ĺ���