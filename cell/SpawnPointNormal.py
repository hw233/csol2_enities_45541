# -*- coding: gb18030 -*-
import BigWorld

from interface.GameObject import GameObject
import SpawnPointScript

import csdefine

#在文件的这一层，我不希望在这个地方做任何的实现，我希望SpawnPointEntity仅提供要迁移的属性定义和方法；
#要实现具体功能性的东西，请去SpawnPointScrip里面去做
#by kenner

class SpawnPointNormal( GameObject ):
	"""
	刷新点控制Entity
	"""
	def __init__( self ):
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPAWN_POINT )
	
	def getScript( self ):
		return SpawnPointScript.getScript( self.spawnType )
		
	def entityDead( self ):
		"""
		Define method.
		怪物死亡通知
		"""
		# 小于0则不复活
		self.getScript().entityDead( self )
		
	def createEntity( self, params = {} ):
		"""
		Define method.
		创建怪物，有参数
		"""
		self.getScript().createEntity( self, params )
	
	def createEntityNormal( self ):
		"""
		Define method.
		创建怪物，无参数
		"""
		self.createEntity()
	
	def destroyEntity( self, params ):
		"""
		Define method.
		销毁怪物
		"""
		self.getScript().destroyEntity( self, params )

	def onTimer( self, controllerID, userData ):
		"""
		BigWorld method.
		"""
		self.getScript().onTimer( self, controllerID, userData )
		
	def onBaseGotCell( self ):
		"""
		BigWorld method.
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		self.getScript().onBaseGotCell( self )
	
	def destroySpawnPoint( self ):
		"""
		define method.
		手动destoy
		"""
		self.getScript().destroySpawnPoint( self )
	
	def getEntityData( self, key, default = None ):
		"""
		获取配置Entity参数的值
		"""
		if self.entityParams.has_key( key ):
			return self.entityParams[ key ]
		
		return default
	
	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		BigWorld method.
		"""
		self.getScript().onEnterTrapExt( self, entity, range, controllerID )
		
	def remoteCallScript( self, methodName, args ):
		"""
		define method
		转发调用Script的一个方式
		"""
		scriptObj = self.getScript()
		
		try:
			method = getattr( scriptObj, methodName )
		except AttributeError, errstr:
			ERROR_MSG( "SpawnPoint %s(%s): has not method %s." % (self.__class__.__name__, scriptObj.__class__.__name__, methodName ) )
			return
			
		args.insert( 0, self ) #把自己插入参数1
		method( *args )
		