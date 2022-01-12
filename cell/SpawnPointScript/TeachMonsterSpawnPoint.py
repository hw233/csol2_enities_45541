# -*- coding:gb18030 -*-

from bwdebug import *
import BigWorld
from SpawnPoint import SpawnPoint
import csconst
from ObjectScripts.GameObjectFactory import g_objFactory

class TeachMonsterSpawnPoint( SpawnPoint ):
	"""
	ʦͽ�������������
	"""
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity )
		args[ "level" ] = int( BigWorld.getSpaceDataFirstForKey( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TEACH_MONSTER_LEVEL ) )
		return args
			
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
			
		monsterCount = BigWorld.getSpaceDataFirstForKey( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, int(monsterCount) - 1 )