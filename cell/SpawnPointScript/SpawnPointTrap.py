# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

class SpawnPointTrap( SpawnPoint ):
	"""
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )