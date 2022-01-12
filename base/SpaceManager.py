# -*- coding: gb18030 -*-
#
# $Id: SpaceManager.py,v 1.36 2008-04-16 05:49:52 phw Exp $

"""
Space Manager class
"""

import Language
import BigWorld
import csconst
import time
import SpaceDomain
from bwdebug import *
import Function
import Language

# domainItem ������ domain entity �Ĵ����ͼ���
class DomainItem:
	def __init__( self, name ):
		self.name = name
		self.base = None

	def createBase( self, domainType, params ):
		"""
		����domainʵ��
		"""
		self.base = BigWorld.createBaseLocally( domainType, params )
		if not self.base:
			ERROR_MSG( "create domain entity error! name:", self.name )
			return


# ����������
class SpaceManager( BigWorld.Base ):
	"""
	����������
	������ͨ�ռ�͸���
	"""
	def __init__( self ):
		BigWorld.Base.__init__(self)

		self._lastSpaceNumber = 0 	# ���ڷ���space��ID
		self._spaceNumbers = []		# ���ڼ�¼�����Ѿ������ space��number �ļ���
		self.domainItems_ = {}		# space domains��like as { spaceDomainKey : DomainItem(), ... }

		BigWorld.globalData["SpaceManager"] = self				# ע�ᵽ���еķ�������
		self._loadConfig( csconst.SPACE_CONFIG_PATH )

	# init
	def _loadConfig( self, configFilePath ):
		"""
		��ʼ�����еĵ�ͼ����
		@param configFileName: String; like as config/server/gameObject/space/space.xml
		"""
		for configFileName in Language.searchConfigFile( [ configFilePath ], ".xml" ):
			spaceConfigSection = Language.openConfigSection(configFileName)
			if spaceConfigSection is None:
				ERROR_MSG( "Space config file %s not find." % configFileName )
				continue
			self._initSpaceDomain( spaceConfigSection )

	def _initSpaceDomain( self, section ):
		"""
		"""
		spaceType = section['className'].asString
		# ������ͼ����
		INFO_MSG( "Creating space domain:", spaceType )
		params = {	"name"		: spaceType,
					"maxCopy"	: section.readInt( "maxCopy" ),		# ��󸱱�ʵ������
					"maxRepeat"	: section.readInt( "maxRepeat" ),		# ÿСʱ�ڣ�����¸����������
				}
		shareDomain = self.getShareDomainItem( section )
		if shareDomain:
			self.domainItems_[spaceType] = shareDomain
		else:
			self.domainItems_[spaceType] = DomainItem( spaceType )
			self.domainItems_[spaceType].createBase( section["DomainType"].asString, params )
		
	def getShareDomainItem( self, section ):
		"""
		��ȡ����domainItem(��Ҫ���в��ָ����Ƕ����ͼ�����ǹ���һ��domain)
		"""
		shareDomainTypes = section.readString( "shareDomain" )
		for t in shareDomainTypes.split( ";" ):
			if self.domainItems_.has_key( t ):
				return self.domainItems_[ t ]
				
		return None

	def getDomainItem( self, spaceType ):
		"""
		��ȡ��spaceType��Ӧ��domainʵ�� û�з���none
		"""
		return self.domainItems_.get( spaceType, None )

	# public:
	def getNewSpaceNumber( self ):
		"""
		��ȡһ��Ψһ��space���
		@return: INT32
		"""
		state = 1
		number = self._lastSpaceNumber
		while state > 0:
			number = ( number + 1 ) % 0x7FFFFFFF
			if not number in self._spaceNumbers:
				state = 0

		self._lastSpaceNumber = number
		self._spaceNumbers.append( number )
		return number

	def createNPCObjectFormBase( self, spaceName, npcID, position, direction, state ):
		"""
		<Define method>
		(Զ��)����һ������ҿ��ƶ��� �ö���ӵ��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.domainItems_[ spaceName ].base.createNPCObjectFormBase( npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, spaceName, npcID, position, direction, state ):
		"""
		<Define method>
		(Զ��)����һ������ҿ��ƶ��� �ö���û��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.domainItems_[ spaceName ].base.createCellNPCObjectFormBase( npcID, position, direction, state )

	def removeSpaceNumber( self, number ):
		"""
		<Define method>
		ɾ��һ��spaceΨһ��ʶ
		@param 	number:		Ψһ��ʶ
		@type 	number:		int32
		"""
		self._spaceNumbers.remove( number )

	def teleportEntity( self, spaceType, position, direction, baseMailbox, params ):
		"""
		<Define method>
		����һ��entity��ָ����space��
		@param spaceType:��ͼ��� "yanhuang",...
		@type spaceType : String,
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		self.domainItems_[spaceType].base.teleportEntity( position, direction, baseMailbox, params )

	def teleportEntityOnLogin( self, spaceType, baseMailbox, params ):
		"""
		<Define method>
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param spaceType:��ͼ��� "yanhuang",...
		@type spaceType : String,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		self.domainItems_[spaceType].base.teleportEntityOnLogin( baseMailbox, params )

	def requestNewSpace( self, spaceType, mailbox, params ):
		"""
		<Define method>
		����һ���µĿռ�
		@param 	spaceType	:	�ռ������ռ�Ĺؼ���
		@type 	spaceType	:	string
		@param 	mailbox		:	ʵ��mailbox: �ռ䴴����ɺ�֪ͨ��ʵ��mailbox ���Mailbox�ϱ�����onRequestCell����
		@type 	mailbox		:	mailbox
		"""
		self.domainItems_[spaceType].base.requestCreateSpace( mailbox, params )

	def queryBossesKilledOfCopyTeam( self, spaceType, querist, teamID ) :
		"""
		<Define method>
		��ѯ������boss��ɱ����
		@type	spaceType : STRING
		@param	spaceType : �ռ��ǣ�className��
		@type	querist : MAILBOX
		@param	querist : ��ѯ�ߣ�������ж��巽��onQueryBossesKilledCallback
		@type	teamID : OBJECT_ID
		@param	teamID : �����ID
		"""
		try :
			self.domainItems_[spaceType].base.queryBossesKilledByTeamID( querist, teamID )
		except Exception, errstr :
			ERROR_MSG( "Error occur on spaceType %s: %s" % ( spaceType, errstr ) )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# �ص�һ����������ʾ������
	
	def remoteCallDomain( self, spaceType, methodName, args ):
		"""
		define method
		ת������Domain��һ����ʽ
		"""
		domainBase = self.domainItems_[ spaceType ].base
		
		try:
			method = getattr( domainBase, methodName )
		except AttributeError, errstr:
			ERROR_MSG( "domain %s(%i): class %s has not method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		method( *args )

#
# $Log: not supported by cvs2svn $
# Revision 1.35  2008/01/28 06:00:33  kebiao
# add method: createNPCObjectFormBase
#
# Revision 1.34  2008/01/25 10:05:01  yangkai
# �����ļ�·���޸�
#
# Revision 1.33  2007/10/10 00:56:22  phw
# method modified: createNPCObject(), �����˴���ʱ���ʲ����ڵı�����bug
#
# Revision 1.32  2007/10/07 07:17:54  phw
# method modified: _loadConfig(), �����˶ԡ�maxRepeat�������Ķ�ȡ
#
# Revision 1.31  2007/10/03 07:44:27  phw
# ��������
# method modified: _loadConfig(), �ڴ���SpaceDomainʱ�����ݶ������
#
# Revision 1.30  2007/09/29 06:02:12  phw
# �����˸����ܺ�����ʵ�ַ�ʽ
#
# Revision 1.29  2007/09/28 02:16:19  yangkai
# �����ļ�·������:
# res/server/config  -->  res/config
#
# Revision 1.28  2007/09/25 01:32:36  kebiao
# �޸�һ��ע��
#
# Revision 1.27  2007/09/22 09:07:10  kebiao
# ���µ�����space���
#
#
#