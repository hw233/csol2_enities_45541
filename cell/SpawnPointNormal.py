# -*- coding: gb18030 -*-
import BigWorld

from interface.GameObject import GameObject
import SpawnPointScript

import csdefine

#���ļ�����һ�㣬�Ҳ�ϣ��������ط����κε�ʵ�֣���ϣ��SpawnPointEntity���ṩҪǨ�Ƶ����Զ���ͷ�����
#Ҫʵ�־��幦���ԵĶ�������ȥSpawnPointScrip����ȥ��
#by kenner

class SpawnPointNormal( GameObject ):
	"""
	ˢ�µ����Entity
	"""
	def __init__( self ):
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPAWN_POINT )
	
	def getScript( self ):
		return SpawnPointScript.getScript( self.spawnType )
		
	def entityDead( self ):
		"""
		Define method.
		��������֪ͨ
		"""
		# С��0�򲻸���
		self.getScript().entityDead( self )
		
	def createEntity( self, params = {} ):
		"""
		Define method.
		��������в���
		"""
		self.getScript().createEntity( self, params )
	
	def createEntityNormal( self ):
		"""
		Define method.
		��������޲���
		"""
		self.createEntity()
	
	def destroyEntity( self, params ):
		"""
		Define method.
		���ٹ���
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
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		self.getScript().onBaseGotCell( self )
	
	def destroySpawnPoint( self ):
		"""
		define method.
		�ֶ�destoy
		"""
		self.getScript().destroySpawnPoint( self )
	
	def getEntityData( self, key, default = None ):
		"""
		��ȡ����Entity������ֵ
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
		ת������Script��һ����ʽ
		"""
		scriptObj = self.getScript()
		
		try:
			method = getattr( scriptObj, methodName )
		except AttributeError, errstr:
			ERROR_MSG( "SpawnPoint %s(%s): has not method %s." % (self.__class__.__name__, scriptObj.__class__.__name__, methodName ) )
			return
			
		args.insert( 0, self ) #���Լ��������1
		method( *args )
		