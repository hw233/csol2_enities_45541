# -*- coding: gb18030 -*-
# CustomDBOperation.py

import BigWorld
from Function import Functor
from bwdebug import *
import csdefine

class ProcedureManager:
	"""
	�洢���̹�����
	"""
	_instance = None
	def __init__( self ):
		"""
		��ʼ��
		"""
		assert self._instance is None,"ProcedureManager is already exist!"

	def updateProcedures( self ):
		"""
		��������Ӵ洢����
		"""
		self.updateRankingProcedures()	# ���а�洢���̸���
		self.updateGameBroadcast()		# ��Ϸ����洢���̸���
		self.updateChangeRoleName()		# ��ҽ�ɫ�����洢����

	def updateChangeRoleName( self ):
		"""
		������Ҹ����洢����
		"""
		sql_drop = """DROP PROCEDURE IF EXISTS `CHANGEROLENAME`;"""		# ������ھ���ɾ���ô洢����
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
		�������а�Ĵ洢����
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
		
		sql_drop = 	"""DROP PROCEDURE IF EXISTS `LEVELRANKING`;"""	# ������ھ���ɾ���ô洢����

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
					END;"""		# �����洢����

		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )


		sql_drop = 	"""DROP PROCEDURE IF EXISTS `MONEYRANKING`;"""		# ������ھ���ɾ���ô洢����

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
					END;"""		# �����洢����

		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `TONGRANKING`;"""		# ������ھ���ɾ���ô洢����

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
					END;""" % csdefine.TONG_DUTY_CHIEF		# �����洢����
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `PKRANKING`;"""		# ������ھ���ɾ���ô洢����

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
					END;"""		# �����洢����
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

		sql_drop = 	"""DROP PROCEDURE IF EXISTS `HONOR`;"""		# ������ھ���ɾ���ô洢����

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
					END;"""		# �����洢����
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )


		sql_drop = 	"""DROP PROCEDURE IF EXISTS `UPDATERANKING`;"""		# ������ھ���ɾ���ô洢����

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
					END;"""		# �����洢����
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

	def updateGameBroadcast( self ):
		"""
		������Ϸ����洢����
		"""
		sql_drop = 	"""DROP PROCEDURE IF EXISTS `GAMEBROADCAST`;"""		# ������ھ���ɾ���ô洢����

		sql_create = """CREATE DEFINER=CURRENT_USER PROCEDURE `GAMEBROADCAST`()
						BEGIN
						delete from custom_GameBroadcast where DateDiff(now(),operationend) > 3;
						update custom_GameBroadcast set mark = 0 where mark = 1;
						update custom_GameBroadcast set mark = 1 where now() < operationend and status != 1;
						END;"""		# �����洢����
		BigWorld.executeRawDatabaseCommand( sql_drop, Functor( self.onDropProcedureCB, sql_create ) )

	def onDropProcedureCB( self, sql_create, result, rows, errstr ):
		"""
		ɾ���洢���̵Ļص�����
		"""
		if errstr:
			# �����洢���̴���
			ERROR_MSG("Drop Procedure Fail! %s " % errstr)
			return
		BigWorld.executeRawDatabaseCommand( sql_create, self.onCreateProcedureCB )

	def onCreateProcedureCB( self, result, rows, errstr ):
		"""
		�����˴洢���̵Ļص�����
		"""
		if errstr:
			# �����洢���̴���
			ERROR_MSG("Create Procedure Fail! %s " % errstr)
			return

	@classmethod
	def instance( self ):
		"""
		��ȡΨһʵ��
		"""
		if not self._instance:
			self._instance = ProcedureManager()
		return self._instance

class IndexManager:
	"""
	���ݿ�������������
	"""
	_instance = None
	def __init__( self ):
		"""
		��ʼ��
		"""
		assert self._instance is None,"IndexManager is already exist!"

	def updateIndex( self ):
		"""
		�����洢����
		"""
		#self.createIndex("tbl_Role_itemsBag_items", "sm_uid" )	# �� tbl_Role_itemsBag_items ���� sm_uid Ϊ��ͨ����
		pass	# ������Ʒ��������������ɷ����������ǳ�����,Ŀǰ���ε��ô����ӿ�,ת������������ʽ������Ʒ������,���ڸ�ģ���������
				# �Ǵ�������������������ʱ������ģ�顣

	def createIndex( self, tableName, column_name ):
		"""
		����һ������,����ñ���ڸ�����,�򲻻ᴴ�����ýӿ�֧�����������
		@param tableName: ����
		@type  tableName: String
		@param column_name: �ֶ��� ��Ҫ�����������,���ֶ����ö��ŷָ�, ��ʽΪ "sm_a,sm_b"
		@type  column_name: String
		"""
		sql_check = """select statistics.index_name from information_schema.statistics where
						statistics.table_name="%s" and
						statistics.index_name="%s" and
						statistics.table_schema=DATABASE()""" % ( tableName, column_name + "_Index")
		BigWorld.executeRawDatabaseCommand( sql_check, Functor( self.onCreateIndexCB, tableName, column_name) )

	def onCreateIndexCB( self, tableName, column_name, result, rows, errstr ):
		"""
		�����������Ļص�����
		"""
		if errstr:
			# �����洢���̴���
			ERROR_MSG("Check Index Fail! %s " % errstr)
			return
		if not result:
			sql_create = "create index `%s` on `%s` (`%s`)" % ( column_name + "_Index", tableName, column_name)
			BigWorld.executeRawDatabaseCommand( sql_create, self.onCreateIndexResultCB )

	def onCreateIndexResultCB( self, result, rows, errstr ):
		"""
		�����˴洢���̵Ļص�����
		"""
		if errstr:
			# �����洢���̴���
			ERROR_MSG("Create Index Fail! %s " % errstr)
			return

	@classmethod
	def instance( self ):
		"""
		��ȡΨһʵ��
		"""
		if not self._instance:
			self._instance = IndexManager()
		return self._instance


g_proceduremanager = ProcedureManager.instance()
g_indexmanager = IndexManager.instance()