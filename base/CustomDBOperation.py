# -*- coding: gb18030 -*-
# CustomDBOperation.py

import BigWorld
from Function import Functor
from bwdebug import *
import csdefine

class ProcedureManager:
	"""
	存储过程管理类
	"""
	_instance = None
	def __init__( self ):
		"""
		初始化
		"""
		assert self._instance is None,"ProcedureManager is already exist!"

	def updateProcedures( self ):
		"""
		创建和添加存储过程
		"""
		self.updateRankingProcedures()	# 排行榜存储过程更新
		self.updateGameBroadcast()		# 游戏公告存储过程更新
		self.updateChangeRoleName()		# 玩家角色改名存储过程

	def updateChangeRoleName( self ):
		"""
		更新玩家改名存储过程
		"""
		sql_drop = """DROP PROCEDURE IF EXISTS `CHANGEROLENAME`;"""		# 如果存在就先删除该存储过程
		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `CHANGEROLENAME`( oldName varchar(255), newName varchar(255) )
						BEGIN
						update tbl_Role set sm_playerName = newName where sm_playerName = oldName;
						update custom_DartTable set sm_playerName = newName where sm_playerName = oldName;
						update custom_MailTable set sm_senderName = newName where sm_senderName = oldName;
						update custom_MailTable set sm_receiverName = newName where sm_receiverName = oldName;
						update custom_PetProcreation set sm_playerName1 = newName where sm_playerName1 = oldName;
						update custom_PetProcreation set sm_playerName2 = newName where sm_playerName2 = oldName;
						update custom_PointCardsTable set sm_buyerName = newName where sm_buyerName = oldName;
						update custom_TeachInfo set sm_playerName = newName where sm_playerName = oldName;
						update custom_TiShouItemTable set sm_roleName = newName where sm_roleName = oldName;
						update custom_TiShouPetTable set sm_roleName = newName where sm_roleName = oldName;
						update custom_TiShouTable set sm_roleName = newName where sm_roleName = oldName;
						update custom_TiShouRecordTable set sm_roleName = newName where sm_roleName = oldName;
						END;
					"""
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

	def updateRankingProcedures( self ):
		"""
		更新排行榜的存储过程
		"""
		sql_drop =	"""DROP PROCEDURE IF EXISTS `COPY_CUSTOM_RANKING`;"""
		
		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `COPY_CUSTOM_RANKING`()
					BEGIN
					INSERT INTO custom_oldRanking 
					select  *  
					from custom_Ranking  order by id ASC;
					
					ALTER TABLE custom_oldRanking AUTO_INCREMENT = 0;
					END;
					"""
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )
		
		sql_drop = 	"""DROP PROCEDURE IF EXISTS `LEVELRANKING`;"""	# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `LEVELRANKING`()
					BEGIN
					
					INSERT INTO custom_Ranking( type, parentID, param1, param2, param3, param4, param5, param6 )
					SELECT 1,
					id,
					(NULL),
					sm_playerName,
					sm_level,
					sm_raceclass&0xf0,
					"",
					(select sm_playerName from tbl_TongEntity where id = tbl_Role.sm_tong_dbID)
					from tbl_Role where sm_grade <= 30 order by sm_level desc limit 20;


					ALTER TABLE custom_Ranking AUTO_INCREMENT = 0;
					END;"""		# 创建存储过程

		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )


		sql_drop = 	"""DROP PROCEDURE IF EXISTS `MONEYRANKING`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `MONEYRANKING`()
					BEGIN
					

					INSERT INTO custom_Ranking( type, parentID, param1, param2, param3, param4, param5 )
					SELECT 2,
					id,
					(NULL),
					sm_playerName,
					sm_money + sm_bankMoney,
					"",
					(select sm_playerName from tbl_TongEntity where id = tbl_Role.sm_tong_dbID)
					from tbl_Role where sm_grade <= 30 order by sm_money + sm_bankMoney desc limit 20;


					ALTER TABLE custom_Ranking AUTO_INCREMENT = 0;
					END;"""		# 创建存储过程

		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `TONGRANKING`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `TONGRANKING`()
					BEGIN
					

					INSERT INTO custom_Ranking( type, parentID, param1, param2, param3, param4, param5, param6 )
					SELECT 3,
					id,
					(NULL),
					sm_playerName,
					sm_level,
					sm_prestige,
					(select sm_playerName from tbl_Role where sm_tong_grade = %i and sm_tong_dbID = tbl_TongEntity.id),
					sm_memberCount
					from tbl_TongEntity order by sm_level desc,sm_prestige desc limit 20;


					ALTER TABLE custom_Ranking AUTO_INCREMENT = 0;
					END;""" % csdefine.TONG_DUTY_CHIEF		# 创建存储过程
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `PKRANKING`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `PKRANKING`()
					BEGIN
					
					INSERT INTO custom_Ranking( type, parentID, param1, param2, param3, param4, param5, param6 )
					SELECT 5,
					tbl_tmp.*
					from
					(select
					id,
					(NULL),
					sm_playerName,
					sm_level,
					sm_raceclass&0xf0,
					sm_homicideNumber,
					sm_deadNumber
					from tbl_Role where sm_grade <= 30 order by sm_homicideNumber desc limit 20 ) as tbl_tmp
					order by sm_homicideNumber desc,sm_deadNumber asc, id asc;

					ALTER TABLE custom_Ranking AUTO_INCREMENT = 0;
					END;"""		# 创建存储过程
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `HONOR`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `HONOR`()
					BEGIN
					
					INSERT INTO custom_Ranking( type, parentID, param1, param2, param3 )
					SELECT 6,
					id,
					(NULL),
					sm_playerName,
					sm_honor
					from tbl_Role where sm_grade <= 30 order by sm_honor desc limit 20;


					ALTER TABLE custom_Ranking AUTO_INCREMENT = 0;
					END;"""		# 创建存储过程
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )


		sql_drop = 	"""DROP PROCEDURE IF EXISTS `UPDATERANKING`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `UPDATERANKING`()
					BEGIN
					TRUNCATE TABLE custom_oldRanking;
					call COPY_CUSTOM_RANKING();
					TRUNCATE TABLE custom_Ranking;
					call LEVELRANKING();
					call MONEYRANKING();
					call TONGRANKING();
					call PKRANKING();
					call HONOR();
					END;"""		# 创建存储过程
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

	def updateGameBroadcast( self ):
		"""
		更新游戏公告存储过程
		"""
		sql_drop = 	"""DROP PROCEDURE IF EXISTS `GAMEBROADCAST`;"""		# 如果存在就先删除该存储过程

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `GAMEBROADCAST`()
						BEGIN
						delete from custom_GameBroadcast where DateDiff(now(),operationend) > 3;
						update custom_GameBroadcast set mark = 0 where mark = 1;
						update custom_GameBroadcast set mark = 1 where now() < operationend and status != 1;
						END;"""		# 创建存储过程
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

	def onDropProcedureCB( self, sql_create, result, rows, errstr ):
		"""
		删除存储过程的回调函数
		"""
		if errstr:
			# 创建存储过程错误
			ERROR_MSG("Drop Procedure Fail! %s " % errstr)
			return
		BigWorld.executeRawDatabaseCommand( sql_create, self.onCreateProcedureCB )

	def onCreateProcedureCB( self, result, rows, errstr ):
		"""
		创建了存储过程的回调函数
		"""
		if errstr:
			# 创建存储过程错误
			ERROR_MSG("Create Procedure Fail! %s " % errstr)
			return

	@classmethod
	def instance( self ):
		"""
		获取唯一实例
		"""
		if not self._instance:
			self._instance = ProcedureManager()
		return self._instance

class IndexManager:
	"""
	数据库表格索引管理类
	"""
	_instance = None
	def __init__( self ):
		"""
		初始化
		"""
		assert self._instance is None,"IndexManager is already exist!"

	def updateIndex( self ):
		"""
		创建存储过程
		"""
		#self.createIndex("tbl_Role_itemsBag_items", "sm_uid" )	# 表 tbl_Role_itemsBag_items 增加 sm_uid 为普通索引
		pass	# 由于物品表增加索引会造成服务器启动非常缓慢,目前屏蔽掉该创建接口,转而采用其他方式增加物品表索引,由于该模块可以用于
				# 非大表的索引创建，所以暂时保留该模块。

	def createIndex( self, tableName, column_name ):
		"""
		创建一个索引,如果该表存在该索引,则不会创建，该接口支持组合索引。
		@param tableName: 表名
		@type  tableName: String
		@param column_name: 字段名 如要创建组合索引,将字段名用逗号分隔, 格式为 "sm_a,sm_b"
		@type  column_name: String
		"""
		sql_check = """select statistics.index_name from information_schema.statistics where
						statistics.table_name="%s" and
						statistics.index_name="%s" and
						statistics.table_schema=DATABASE()""" % ( tableName, column_name + "_Index")
		BigWorld.executeRawDatabaseCommand( sql_check, Functor( self.onCreateIndexCB, tableName, column_name) )

	def onCreateIndexCB( self, tableName, column_name, result, rows, errstr ):
		"""
		创建了索引的回调函数
		"""
		if errstr:
			# 创建存储过程错误
			ERROR_MSG("Check Index Fail! %s " % errstr)
			return
		if not result:
			sql_create = "create index `%s` on `%s` (`%s`)" % ( column_name + "_Index", tableName, column_name)
			BigWorld.executeRawDatabaseCommand( sql_create, self.onCreateIndexResultCB )

	def onCreateIndexResultCB( self, result, rows, errstr ):
		"""
		创建了存储过程的回调函数
		"""
		if errstr:
			# 创建存储过程错误
			ERROR_MSG("Create Index Fail! %s " % errstr)
			return

	@classmethod
	def instance( self ):
		"""
		获取唯一实例
		"""
		if not self._instance:
			self._instance = IndexManager()
		return self._instance


g_proceduremanager = ProcedureManager.instance()
g_indexmanager = IndexManager.instance()