# -*- coding: gb18030 -*-

from SpawnPointCopyTemplate import SpawnPointCopyTemplate
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyFangShou( SpawnPointCopyTemplate ):
	"""
	���ظ���ˢ�µ㣬entityName��������n�ֹ���className����ͬclassName֮���ÿո�ֿ���
	����֪ͨˢ��ʱ�ᰴ����ˢ����n�ֹ֣��� n+1 ��֪ͨˢ�ֻ�ˢ����һ�ֹ֡�
	"""
	def __init__( self ) :
		SpawnPointCopyTemplate.__init__( self )
	
	def initEntity( self, selfEntity ) :
		SpawnPointCopyTemplate.initEntity( self, selfEntity )
		selfEntity.setTemp( "currentMonsterIndex", 0 )

	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		entityList = selfEntity.entityName.split()
		currentMonsterIndex = selfEntity.queryTemp( "currentMonsterIndex", 0 )
		args = SpawnPointCopyTemplate.getEntityArgs( self, selfEntity, params )
		if currentMonsterIndex < len( entityList ) :
			selfEntity.setTemp( "currentMonsterIndex", currentMonsterIndex + 1 )
		else :
			selfEntity.setTemp( "currentMonsterIndex", 0 )
			currentMonsterIndex = 0
		args[ "className" ] = entityList[ currentMonsterIndex ]
		return args
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		֪ͨˢ������
		"""
		SpawnPointCopyTemplate.createEntity( self, selfEntity, params )
