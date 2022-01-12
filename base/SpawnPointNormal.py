# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject
import SpawnPointScript

#���ļ�����һ�㣬�Ҳ�ϣ��������ط����κε�ʵ�֣���ϣ��SpawnPointEntityֻ���ṩ�ӿڣ��Լ�ҪǨ�Ƶ����Զ���ͷ�����
#Ҫʵ�־��幦���ԵĶ�������ȥSpawnPointScrip����ȥ��
#by kenner

class SpawnPointNormal( BigWorld.Base, GameObject ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		if hasattr( self, "cellData" ):
			self.spawnType = self.cellData["spawnType"]
			
		GameObject.__init__( self )
		
		self.getScript().initEntity( self )
		
	def getScript( self ):
		return SpawnPointScript.getScript( self.spawnType )
	
	def getSpawnType( self ):
		return self.spawnType
	
	def createBaseEntity( self, entityName, params ):
		"""
		virtual method.
		ˢ����base�Ĺ���
		"""
		self.getScript().createBaseEntity( self, entityName, params )
		
	def onLoseCell( self ):
		self.getScript().onLoseCell( self )
	
	def onGetCell( self ):
		self.getScript().onGetCell( self )
