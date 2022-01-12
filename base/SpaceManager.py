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

# domainItem ：负责 domain entity 的创建和加载
class DomainItem:
	def __init__( self, name ):
		self.name = name
		self.base = None

	def createBase( self, domainType, params ):
		"""
		创建domain实体
		"""
		self.base = BigWorld.createBaseLocally( domainType, params )
		if not self.base:
			ERROR_MSG( "create domain entity error! name:", self.name )
			return


# 场景管理器
class SpaceManager( BigWorld.Base ):
	"""
	场景管理器
	控制普通空间和副本
	"""
	def __init__( self ):
		BigWorld.Base.__init__(self)

		self._lastSpaceNumber = 0 	# 用于分配space的ID
		self._spaceNumbers = []		# 用于记录所有已经分配的 space的number 的集合
		self.domainItems_ = {}		# space domains，like as { spaceDomainKey : DomainItem(), ... }

		BigWorld.globalData["SpaceManager"] = self				# 注册到所有的服务器中
		self._loadConfig( csconst.SPACE_CONFIG_PATH )

	# init
	def _loadConfig( self, configFilePath ):
		"""
		初始化所有的地图领域
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
		# 创建地图领域
		INFO_MSG( "Creating space domain:", spaceType )
		params = {	"name"		: spaceType,
					"maxCopy"	: section.readInt( "maxCopy" ),		# 最大副本实例数量
					"maxRepeat"	: section.readInt( "maxRepeat" ),		# 每小时内，最大新副本进入次数
				}
		shareDomain = self.getShareDomainItem( section )
		if shareDomain:
			self.domainItems_[spaceType] = shareDomain
		else:
			self.domainItems_[spaceType] = DomainItem( spaceType )
			self.domainItems_[spaceType].createBase( section["DomainType"].asString, params )
		
	def getShareDomainItem( self, section ):
		"""
		获取共享domainItem(主要是有部分副本是多个地图，他们共享一个domain)
		"""
		shareDomainTypes = section.readString( "shareDomain" )
		for t in shareDomainTypes.split( ";" ):
			if self.domainItems_.has_key( t ):
				return self.domainItems_[ t ]
				
		return None

	def getDomainItem( self, spaceType ):
		"""
		获取与spaceType对应的domain实例 没有返回none
		"""
		return self.domainItems_.get( spaceType, None )

	# public:
	def getNewSpaceNumber( self ):
		"""
		获取一个唯一的space编号
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
		(远程)创建一个非玩家控制对象 该对象拥有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.domainItems_[ spaceName ].base.createNPCObjectFormBase( npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, spaceName, npcID, position, direction, state ):
		"""
		<Define method>
		(远程)创建一个非玩家控制对象 该对象没有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.domainItems_[ spaceName ].base.createCellNPCObjectFormBase( npcID, position, direction, state )

	def removeSpaceNumber( self, number ):
		"""
		<Define method>
		删除一个space唯一标识
		@param 	number:		唯一标识
		@type 	number:		int32
		"""
		self._spaceNumbers.remove( number )

	def teleportEntity( self, spaceType, position, direction, baseMailbox, params ):
		"""
		<Define method>
		传送一个entity到指定的space中
		@param spaceType:地图类别 "yanhuang",...
		@type spaceType : String,
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		self.domainItems_[spaceType].base.teleportEntity( position, direction, baseMailbox, params )

	def teleportEntityOnLogin( self, spaceType, baseMailbox, params ):
		"""
		<Define method>
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param spaceType:地图类别 "yanhuang",...
		@type spaceType : String,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		self.domainItems_[spaceType].base.teleportEntityOnLogin( baseMailbox, params )

	def requestNewSpace( self, spaceType, mailbox, params ):
		"""
		<Define method>
		创建一个新的空间
		@param 	spaceType	:	空间名，空间的关键字
		@type 	spaceType	:	string
		@param 	mailbox		:	实体mailbox: 空间创建完成后通知的实体mailbox 这个Mailbox上必需有onRequestCell方法
		@type 	mailbox		:	mailbox
		"""
		self.domainItems_[spaceType].base.requestCreateSpace( mailbox, params )

	def queryBossesKilledOfCopyTeam( self, spaceType, querist, teamID ) :
		"""
		<Define method>
		查询副本的boss击杀数量
		@type	spaceType : STRING
		@param	spaceType : 空间标记（className）
		@type	querist : MAILBOX
		@param	querist : 查询者，必须带有定义方法onQueryBossesKilledCallback
		@type	teamID : OBJECT_ID
		@param	teamID : 队伍的ID
		"""
		try :
			self.domainItems_[spaceType].base.queryBossesKilledByTeamID( querist, teamID )
		except Exception, errstr :
			ERROR_MSG( "Error occur on spaceType %s: %s" % ( spaceType, errstr ) )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# 回调一个负数，表示出错了
	
	def remoteCallDomain( self, spaceType, methodName, args ):
		"""
		define method
		转发调用Domain的一个方式
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
# 配置文件路径修改
#
# Revision 1.33  2007/10/10 00:56:22  phw
# method modified: createNPCObject(), 修正了创建时访问不存在的变量的bug
#
# Revision 1.32  2007/10/07 07:17:54  phw
# method modified: _loadConfig(), 加入了对“maxRepeat”参数的读取
#
# Revision 1.31  2007/10/03 07:44:27  phw
# 代码整理
# method modified: _loadConfig(), 在创建SpaceDomain时，传递额外参数
#
# Revision 1.30  2007/09/29 06:02:12  phw
# 调整了各功能函数的实现方式
#
# Revision 1.29  2007/09/28 02:16:19  yangkai
# 配置文件路径更改:
# res/server/config  -->  res/config
#
# Revision 1.28  2007/09/25 01:32:36  kebiao
# 修改一处注释
#
# Revision 1.27  2007/09/22 09:07:10  kebiao
# 重新调整了space设计
#
#
#