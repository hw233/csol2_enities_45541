# -*- coding: gb18030 -*-

from SpawnPointCopyTemplate import SpawnPointCopyTemplate
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointCopyFangShou( SpawnPointCopyTemplate ):
	"""
	防守副本刷新点，entityName里面配了n种怪物className，不同className之间用空格分开，
	当被通知刷怪时会按次序刷出这n种怪，第 n+1 次通知刷怪会刷出第一种怪。
	"""
	def __init__( self ) :
		SpawnPointCopyTemplate.__init__( self )
	
	def initEntity( self, selfEntity ) :
		SpawnPointCopyTemplate.initEntity( self, selfEntity )
		selfEntity.setTemp( "currentMonsterIndex", 0 )

	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
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
		通知刷出怪物
		"""
		SpawnPointCopyTemplate.createEntity( self, selfEntity, params )
