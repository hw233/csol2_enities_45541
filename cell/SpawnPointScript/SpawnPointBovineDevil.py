# -*- coding: gb18030 -*-
import BigWorld
from SpawnPointNormalActivity import SpawnPointNormalActivity

class SpawnPointBovineDevil( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "BovineDevilMgr" )
		#selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )

	def getEntityArgs( self, selfEntity, params ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPointNormalActivity.getEntityArgs( self, selfEntity, params )
		
		type = params.get( "type", 0 )
		className = 0
		classNameList = selfEntity.entityName.split(";")
		if classNameList and type < len( classNameList ):
			className = classNameList[ type ]
			
		args[ "className" ] = className
		return args
