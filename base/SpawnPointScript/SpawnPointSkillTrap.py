# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *

from SpawnPoint import SpawnPoint

class SpawnPointSkillTrap( SpawnPoint ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		if hasattr( self, "cellData" ):
			self.className = self.cellData["entityName"]
		SpawnPoint.initEntity( self, selfEntity )
		
	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return self.className
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		entityParams = {}
		entityParams[ "radius" ] = params[ "radius" ].asInt
		entityParams[ "enterSpell" ] = params[ "enterSpell" ].asString
		entityParams[ "leaveSpell" ] = params[ "leaveSpell" ].asString
		entityParams[ "destroySpell" ] = params[ "destroySpell" ].asString
		entityParams[ "modelNumber" ] = params[ "modelNumber" ].asString
		entityParams[ "modelScale" ] = params[ "modelScale" ].asFloat
		entityParams[ "repeattime" ] = params[ "repeattime" ].asInt
		entityParams[ "lifetime" ] = params[ "lifetime" ].asInt
		entityParams[ "isDisposable" ] =params[ "isDisposable" ].asInt
		return entityParams
