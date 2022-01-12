# -*- coding: gb18030 -*-
#
# written by wangshufeng

import BigWorld
import csconst
import Const
from bwdebug import *


class RelationMgr( BigWorld.Base ):
	"""
	玩家关系uid管理：
	
	玩家关系的设计：
	自定义一张db表custom_Relation来存储世界中玩家的关系，其中每一条记录表示两个玩家关系。
	记录中有一个字段relationStatus表示此2个玩家的关系状态，relationStatus是一个uint32数据，
	右起前2个字节表示sm_playerDBID1的玩家关系状态，后2字节表示sm_playerDBID2的关系状态。
	由于双方玩家都有可能同时写这条记录有可能造成前者被覆盖，因此在更新关系状态时使用仅更新relationStatus中的某一个位的方式，
	如此就算双方同时更新此数据后者也不会覆盖掉前者的更改。
	每一条记录都有唯一的一个uid(int32)，玩家更新关系状态时都根据uid来定位关系数据。uid的生成规则如下：
	uid由uidFactory分配，从1开始，给个baseApp每次分配100个uid资源，每个baseApp的uid资源少于10个时会向uidFactory再次申请。
	每次服务器重启都查询custom_Relation，找出最大的uid，以此作为uid分配的起始编号。每次baseApp没用完uid都会再次申请，
	会造成uid资源的冗余，忽略这个冗余。
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.maxUID = 0			# 当前最大的uid
		self.intializeFinish = False	# 是否初始化完毕
		self.registerGlobally( "RelationMgr", self.registerGloballyCB )
		self.createTable()
		
	def registerGloballyCB( self, succeeded ):
		"""
		注册全局实例的回调
		"""
		if not succeeded:
			self.registerGlobally( "RelationMgr", self.registerGloballyCB )
			
	def createTable( self ):
		"""
		创建custom_Relation表
		
		`sm_playerDBID1` 玩家1的databaseID
		`sm_playerDBID2` 玩家2的databaseID
		`sm_relationStatus` 玩家1和玩家2的关系状态
		`sm_friendlyValue` 玩家1和玩家2的友好度
		`sm_uid` 每条关系的唯一id
		`sm_param` 关系额外扩展字段，设置此字段的原因是结拜系统需要存储结拜称号，有此字段也可以存储其他关系额外的数据。
		
		sm_relationStatus是一个UINT32数据。左到右，前16位的位模式表示playerDBID1的关系状态
		后16位的位模式表示playerDBID2的关系状态
		"""
		# 玩家关系表格
		sqlSentence = """CREATE TABLE IF NOT EXISTS `custom_Relation` (
						`id` bigint(20) NOT NULL AUTO_INCREMENT,
						`sm_playerDBID1` BIGINT(20) UNSIGNED NOT NULL,
						`sm_playerDBID2` BIGINT(20) UNSIGNED NOT NULL,
						`sm_relationStatus` int(32) unsigned NOT NULL,
						`sm_friendlyValue` int(32) unsigned NOT NULL default 0,
						`sm_uid` int(32) unsigned NOT NULL,
						`sm_param` text,
						PRIMARY KEY (`id`),
						key (sm_uid),
						key `sm_playerDBID1Index` (sm_playerDBID1),
						key `sm_playerDBID2Index` (sm_playerDBID2)
						)ENGINE=InnoDB;
						"""
		BigWorld.executeRawDatabaseCommand( sqlSentence, self._createTableCB )
		
	def _createTableCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "create custom_Relation error:%s." % errstr )
			return
		BigWorld.executeRawDatabaseCommand( "select max(sm_uid) from custom_Relation;", self.initializeCB )
		
	def initializeCB( self, result, rows, errstr ):
		if errstr:
			ERROR_MSG( "RelationMgr initialize:%s." % errstr )
			return
		DEBUG_MSG( result )
		if result[0][0] is not None:	# 一开始是空表
			self.maxUID = int( result[0][0] )
		self.intializeFinish = True
		# 轮循一次BigWorld.globalBases以查找所有的已注册的base entity发送relationUID
		for k, baseEntityMB in BigWorld.globalBases.items():
			if not isinstance( k, str ) or not k.startswith( csconst.C_PREFIX_GBAE ):
				continue
			self.requestRelationUID( baseEntityMB )
			
	def requestRelationUID( self, baseEntityMB ):
		"""
		Define method.
		baseEntity请求uid.
		此时有可能UIDFactory刚刚初始化好并已经向baseEntity发送了UID，不妨再发。
		
		@param baseEntityMB : baseEntityMB的mailbox
		"""
		if not self.intializeFinish:		# 还没初始化好，请求不成功，初始化完成后会主动给所有的baseApp entity发送relationUID
			return
		minUID = self.maxUID + 1
		self.maxUID += Const.RELATION_UID_SAND_MAX_COUNT
		baseEntityMB.receiveRelationUID( minUID )
		
		