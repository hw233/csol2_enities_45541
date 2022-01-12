# -*- coding:gb18030 -*-

# ��ұ���������Ϣ��¼����Щ��Ϣ����������ڼ�ֻ�ᱻ��ѯһ�Σ�ÿ�β���������ֻ�豣��һ�Ρ�
#
# ���磺
# ���˾�������Ӿ�������Ὰ����
# �ϴβ�����û��֣�ABCD
# �ۼƲ�����û��֣�ABCD
#
# �����ᣬ�����̨�������̨:
# �ϴβ���������Σ�32ǿ/16ǿ/8ǿ/4ǿ/����/�ھ� 
# �����ò������Σ�32ǿ/16ǿ/8ǿ/4ǿ/����/�ھ�
#
# sm_param1��sm_param2���Ը��ݱ�����������ͬ�Ľ��͡��������Ͷ�����csdefine�е�MATCH_TYPE_***
# �����������û������Ĺ滮��Ҳû�����õ���ƣ�ͬʱ��ģ�鲻����̫�����չ��Ҫ����ʵ�ֵ�ǰ�ı������ݴ洢��ѯ���ɡ�


import BigWorld
from bwdebug import *
import csdefine
from Function import Functor

# ����һ����¼��sql���
sqlCmdInsert = "insert into custom_RoleMatchRecord set sm_playerDBID = %i, sm_matchType = %i, sm_param1 = %i, sm_param2 = %i, sm_time = now();"
# ���¾����������Ϣ��sql���
sqlCmdUpdateCpt = "update custom_RoleMatchRecord set sm_param1 = %i, sm_param2 = sm_param2 + %i, sm_time = now() where sm_playerDBID = %i and sm_matchType = %i;"
# ������̨�������Ϣ��sql���
sqlCmdUpdateAba = "update custom_RoleMatchRecord set sm_param1 = %i, sm_param2 = if( %i < sm_param2, %i, sm_param2 ), sm_time = now() where sm_playerDBID = %i and sm_matchType = %i;"
# ��ѯ������Ϣ��sql���
sqlCmdQuery = "select sm_matchType, sm_param1, sm_param2 from custom_RoleMatchRecord where sm_playerDBID = %i;"

cptMatchTypes = ( csdefine.MATCH_TYPE_PERSON_COMPETITION, csdefine.MATCH_TYPE_TEAM_COMPETITION, csdefine.MATCH_TYPE_TONG_COMPETITION )	# ���������������ͼ���
abaMatchTypes = ( csdefine.MATCH_TYPE_PERSON_ABA, csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_TONG_ABA )							# ��̨�����������ͼ���

def getUpdateCmd( playerDBID, matchType, scoreOrRound ):	# ���ɸ��±�����־��sql���
	if matchType in cptMatchTypes:		# ��������
		return sqlCmdUpdateCpt % ( scoreOrRound, scoreOrRound, playerDBID, matchType )
	else:								# ��������̨����
		return sqlCmdUpdateAba % ( scoreOrRound, scoreOrRound, scoreOrRound, playerDBID, matchType )
		
def createTable():
	"""
	@sm_playerDBID : ��ҵ�dbid
	@sm_matchType : �����
	@sm_param1 : ���־����1�����磺�ϴβ�����û��� �� �ϴβ����������
	@sm_param2 : ���־����2�����磺�ۼƲ�����û��� �� �����ò�������
	@sm_time : ʱ��������±�����¼ʱ���ֶλᱻ�����Ա�����¼�Ĵ��ڡ�������µı�������������Ѿ����ڵ�����һ��ʱ��
				��¼���ᱻ���ĵ��½ű�����Ϊ�����ڴ˽�ɫ�ļ�¼������һ���ظ��ļ�¼��
	"""
	sqlCmd = """CREATE TABLE IF NOT EXISTS `custom_RoleMatchRecord` (
					`id` bigint(20) NOT NULL AUTO_INCREMENT,
					`sm_playerDBID` BIGINT(20) UNSIGNED NOT NULL,
					`sm_matchType` TINYINT UNSIGNED NOT NULL,
					`sm_param1` int(32) NOT NULL default 0,
					`sm_param2` int(32) NOT NULL default 0,
					`sm_time` TIMESTAMP(8),
					PRIMARY KEY (`id`),
					key (sm_playerDBID),
					key (sm_matchType)
					)ENGINE=InnoDB;
					"""
	BigWorld.executeRawDatabaseCommand( sqlCmd, createTableCB )
	
def createTableCB( result, rows, errstr ):
	if errstr:
		ERROR_MSG( "create custom_RoleMatchRecord error:%s." % errstr )
		return
	INFO_MSG( "create custom_RoleMatchRecord success." )
	
def update( playerDBID, matchType, scoreOrRound, playerBase = None ):	# ���±�������
	sqlCmd = getUpdateCmd( playerDBID, matchType, scoreOrRound )
	BigWorld.executeRawDatabaseCommand( sqlCmd, Functor( updateCB, playerDBID, playerBase, matchType, scoreOrRound ) )
	
def updateCB( playerDBID, playerBase, matchType, scoreOrRound, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "update>>>( playerDBID:%i,matchType:%i,scoreOrRound:%i ):%s" % ( playerDBID, matchType, scoreOrRound, errstr ) )
		return
	if rows == 0:	# û����Ӧ�ļ�¼����ô��������ҵ���ؼ�¼
		sqlCmd = sqlCmdInsert % ( playerDBID, matchType, scoreOrRound, scoreOrRound )
		BigWorld.executeRawDatabaseCommand( sqlCmd, Functor( insertCB, playerDBID, playerBase, matchType, scoreOrRound ) )
		return
	if playerBase:
		playerBase.client.updateMatchRecord( matchType, scoreOrRound )
		
def insertCB( playerDBID, playerBase, matchType, scoreOrRound, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "insert>>>( playerDBID:%i,matchType:%i,scoreOrRound:%i ):%s" % ( playerDBID, matchType, scoreOrRound, errstr ) )
		return
	if playerBase:
		playerBase.client.initMatchRecord( matchType, scoreOrRound, scoreOrRound )
		
def query( playerBase ):	# ��Ҳ�ѯ���б�����־
	sqlCmd = sqlCmdQuery % playerBase.databaseID
	BigWorld.executeRawDatabaseCommand( sqlCmd, Functor( queryCB, playerBase ) )
	
def queryCB( playerBase, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>playerDBID:%i:%s" % ( playerBase.databaseID, errstr ) )
		return
	if not result:
		DEBUG_MSG( "there is not result for player:%i." % playerBase.databaseID )
		return
	for matchType, param1, param2 in result:	# Ŀǰÿ����������6��
		playerBase.client.initMatchRecord( int( matchType ), int( param1 ), int( param2 ) )
