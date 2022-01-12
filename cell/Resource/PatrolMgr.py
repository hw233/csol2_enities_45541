# -*- coding: gb18030 -*-
#
# $Id: PatrolMgr.py,v 1.3 2008-05-26 03:37:37 kebiao Exp $

"""
Ѳ�ߵ���� kebiao
"""

from bwdebug import *
import Language
import Function
import ResMgr

class PatrolMgr:
	"""
	Ѳ�����ݹ���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert PatrolMgr._instance is None
		self._patrolUserStrings = {} # Ѳ�ߵ����
		self._customNPCPatrol = {} # �Զ���NPCѰ·����
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
		files = Function.searchFile( [configPath], ".graph" )			# ��ȡ�õ�����·���������ļ�
		
		for path in files:
			subsect = ResMgr.openSection( path )
			assert subsect is not None, "open %s false." % path
			for node in subsect.values():
				if node.has_key( "userString" ):
					self.registerUserString( path, node.name, node["userString"].asString )
				else:
					ERROR_MSG( "The file %s has no key 'userString', perhaps the file is wrong." % path )
					continue
			# ��ȡ�����رմ򿪵��ļ�
			ResMgr.purge( path )

	def loadCustomNPCPatrol( self, configPath ):
		"""
		"""
		if len( configPath ) <= 0:
			return
		files = Language.searchConfigFile( [configPath], ".xml" )			# ��ȡ�õ�����·���������ļ�
		
		for path in files:
			subsect = Language.openConfigSection( path )
			assert subsect is not None, "open %s false." % path
			for node in subsect.values():
				assert len( node[ "patrolPathNode" ].asString ) > 0 and len( node[ "patrolList" ].asString ) > 0, "patrol config. npc %s error. patrolList or patrolPathNode is Null." % node.name
				d = { "patrolPathNode" : node[ "patrolPathNode" ].asString }
				d[ "patrolList" ] = node[ "patrolList" ].asString
				self._customNPCPatrol[ node.name ] = d
			# ��ȡ�����رմ򿪵��ļ�
			Language.purgeConfig( path )
			
	def registerUserString( self, path, nodeName, userString ):
		"""
		ע��ýڵ�Ĳ���
		"""
		if len( nodeName ) <= 0 or len( userString ) <= 0:
			return
		if self._patrolUserStrings.has_key( nodeName.lower() ):
			ERROR_MSG( "%s this node %s is exist! userString: %s" % ( path, nodeName, userString ) )		#�ֶ�������������ͬ�ĵ�
			return
		self._patrolUserStrings[ nodeName.lower() ] = int( userString )
	
	def getUserString( self, nodeName ):
		"""
		��ȡ�õ��ϵ��Զ������
		"""
		if not self._patrolUserStrings.has_key( nodeName.lower() ):
			return -1
		return self._patrolUserStrings[ nodeName.lower() ]
		
	def getPatrolData( self, npcID ):
		"""
		��ȡ��ӦnpcID���Զ���Ѳ����Ϣ
		@rtype : û���ҵ����� None ���򷵻� { patrolPathNode:xxx, patrolList:xxx }
		"""
		if self._customNPCPatrol.has_key( npcID ):
			return self._customNPCPatrol[ npcID ]
		return None
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/05/26 03:37:09  kebiao
# ȥ��һ�����õ�����Ϣ
#
# Revision 1.1  2008/03/07 06:38:38  kebiao
# ���Ѳ����ع���
#
#
