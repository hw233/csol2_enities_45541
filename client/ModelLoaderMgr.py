# -*- coding: gb18030 -*-
#
# SourceLoaderMgr.py
#
# 资源加载和下载管理器
#

import BigWorld
import Timer
import ResMgr
import csol
from Function import Functor
from gbref import rds
import sys
from bwdebug import *
from config.client.wdResource import vModel
import event.EventCenter as ECenter

RESOURCE_CHECK_INTERVAL = 1.0   # 侦测timer时间间隔1.0s

class ModelLoaderMgr :
	"""
	模型资源加载
	"""
	__instance = None
	def __init__( self ):
		assert ModelLoaderMgr.__instance is None
		self.sourcedict = {}
		self.entitiesList = []
	
	@classmethod
	def instance( self ):
		if self.__instance is None:
			self.__instance = ModelLoaderMgr()
		return self.__instance

	
	def getSource( self, sourceName ,entityID ):
		if not self.query( sourceName ):
			self.createDefaultModel( entityID )
			self.requstSource( sourceName, entityID )				# 申请资源下载
			self.entitiesList.append( entityID )
	
	def createDefaultModel( self, entityID ):
		model = rds.npcModel.createDefaultModel( Functor( self.onModelLoad, entityID ) )
		
	def onModelLoad( self, entityID, model ):
		if model:
			entity = BigWorld.entities.get( entityID )
			if entity and ( not entity.getModel() ):
				entity.setModel( model )
				entity.flushAttachments_()

	def query( self, source ):
		"""
		"""
		value = False
		try:
			data = vModel.Datas
			key = source.split("/")[1] 
			for i in data[key]:
				value = True
				if csol.isFileAtLocal( i ) <= 0:
					value = False
					break
		except:
			DEBUG_MSG( "monsterLoader key error:%s" %key )
			value = True
		return value

	def query_tick( self, source, entityID ):
		"""
		资源侦测Timer
		"""
		if self.query( source ):
			if self.sourcedict.has_key( source ):
				Timer.cancel( self.sourcedict.pop( source ) )
			entity_ = BigWorld.entities.get( entityID )
			if entity_ and hasattr( entity_, "createModel" ) and \
				entity_.model and  not source in entity_.model.sources :
					for entityID in self.entitiesList[:]:
						entity = BigWorld.entities.get( entityID )
						if not entity:
							self.entitiesList.remove( entityID )
						elif entity.modelNumber == entity_.modelNumber:
							self.entitiesList.remove( entityID )
							model = BigWorld.Model( source )
							entity.setModel( model )
							entity.flushAttachments_()
	
	def requstSource( self, source, entityID ):
		"""
		资源下载
		"""
		try:
			data = vModel.Datas
			key = source.split("/")[1] 
			for i in data[key]:
				csol.addFileToQueue( i, 7 )
			if not self.sourcedict.has_key( source ):
				self.sourcedict[ source ]  = Timer.addTimer( RESOURCE_CHECK_INTERVAL, RESOURCE_CHECK_INTERVAL, Functor( self.query_tick, source, entityID ) )
		except:
			if self.sourcedict.has_key( source):
				Timer.cancel( self.sourcedict.pop( source ) )
