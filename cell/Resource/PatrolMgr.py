# -*- coding: gb18030 -*-
#
# $Id: PatrolMgr.py,v 1.3 2008-05-26 03:37:37 kebiao Exp $

"""
巡逻点参数 kebiao
"""

from bwdebug import *
import Language
import Function
import ResMgr

class PatrolMgr:
	"""
	巡逻数据管理
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert PatrolMgr._instance is None
		self._patrolUserStrings = {} # 巡逻点参数
		self._customNPCPatrol = {} # 自定义NPC寻路数据
		PatrolMgr._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if PatrolMgr._instance is None:
			PatrolMgr._instance = PatrolMgr()
		return PatrolMgr._instance
		
	def loadUserString( self, configPath ):
		"""
		"""
		if len( configPath ) <= 0:
			return
		files = Function.searchFile( [configPath], ".graph" )			# 从取得的配置路径中搜索文件
		
		for path in files:
			subsect = ResMgr.openSection( path )
			assert subsect is not None, "open %s false." % path
			for node in subsect.values():
				if node.has_key( "userString" ):
					self.registerUserString( path, node.name, node["userString"].asString )
				else:
					ERROR_MSG( "The file %s has no key 'userString', perhaps the file is wrong." % path )
					continue
			# 读取完毕则关闭打开的文件
			ResMgr.purge( path )

	def loadCustomNPCPatrol( self, configPath ):
		"""
		"""
		if len( configPath ) <= 0:
			return
		files = Language.searchConfigFile( [configPath], ".xml" )			# 从取得的配置路径中搜索文件
		
		for path in files:
			subsect = Language.openConfigSection( path )
			assert subsect is not None, "open %s false." % path
			for node in subsect.values():
				assert len( node[ "patrolPathNode" ].asString ) > 0 and len( node[ "patrolList" ].asString ) > 0, "patrol config. npc %s error. patrolList or patrolPathNode is Null." % node.name
				d = { "patrolPathNode" : node[ "patrolPathNode" ].asString }
				d[ "patrolList" ] = node[ "patrolList" ].asString
				self._customNPCPatrol[ node.name ] = d
			# 读取完毕则关闭打开的文件
			Language.purgeConfig( path )
			
	def registerUserString( self, path, nodeName, userString ):
		"""
		注册该节点的参数
		"""
		if len( nodeName ) <= 0 or len( userString ) <= 0:
			return
		if self._patrolUserStrings.has_key( nodeName.lower() ):
			ERROR_MSG( "%s this node %s is exist! userString: %s" % ( path, nodeName, userString ) )		#手动复制了名字相同的点
			return
		self._patrolUserStrings[ nodeName.lower() ] = int( userString )
	
	def getUserString( self, nodeName ):
		"""
		获取该点上的自定义参数
		"""
		if not self._patrolUserStrings.has_key( nodeName.lower() ):
			return -1
		return self._patrolUserStrings[ nodeName.lower() ]
		
	def getPatrolData( self, npcID ):
		"""
		获取对应npcID的自定义巡逻信息
		@rtype : 没有找到返回 None 否则返回 { patrolPathNode:xxx, patrolList:xxx }
		"""
		if self._customNPCPatrol.has_key( npcID ):
			return self._customNPCPatrol[ npcID ]
		return None
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/05/26 03:37:09  kebiao
# 去掉一个无用调试信息
#
# Revision 1.1  2008/03/07 06:38:38  kebiao
# 添加巡逻相关功能
#
#
