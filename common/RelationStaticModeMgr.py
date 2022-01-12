# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
from SmartImport import smartImport
import RelationStaticObjImpl
import csdefine
import csconst
from config.CombatCampRelationConfig import Datas as campRelationDatas

class RelationStaticModeMgr:
	"""
	静态关系模式管理器
	"""
	_instance = None
	def __init__( self ):
		assert RelationStaticModeMgr._instance is None
		self.relationInstanceDict = {}
		RelationStaticModeMgr._instance = self
		
	def initCampRelationCfg( self ):
		"""
		初始化普通阵营关系的配置
		"""
		friendRelationList = []
		neutralRelationList = []
		antagonizeRelationList = []
		for type,relationList in campRelationDatas.iteritems():
			if type == csdefine.RELATION_FRIEND:
				friendRelationList = relationList
			elif type == csdefine.RELATION_NEUTRALLY:
				neutralRelationList = relationList
			elif type == csdefine.RELATION_ANTAGONIZE:
				antagonizeRelationList = relationList
			else:
				ERROR_MSG( "relation initialize Error. type is %s, relationList is %s"%( type, relationList ) )
		inst = RelationStaticObjImpl.createRelationObjCamp( friendRelationList, neutralRelationList, antagonizeRelationList )
		self.relationInstanceDict[ csdefine.RELATION_STATIC_CAMP ] = inst
		pass
		
	def createRelationInstance( self ):
		"""
		创建相关的关系实例
		"""
		for type in csconst.RELATION_TYPE_STATIC_SPACE:
			inst = RelationStaticObjImpl.createRelationObjSpace( type )
			self.relationInstanceDict[ type ] = inst
		pass
		
	def getRelationInsFromType( self, type ):
		"""
		根据类型得到相关的关系实例
		"""
		return self.relationInstanceDict[ type ]
		pass
		
	@staticmethod
	def instance():
		"""
		"""
		if RelationStaticModeMgr._instance is None:
			RelationStaticModeMgr._instance = RelationStaticModeMgr()
		return RelationStaticModeMgr._instance