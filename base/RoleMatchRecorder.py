# -*- coding:gb18030 -*-

# 玩家比赛额外信息记录，这些信息在玩家在线期间只会被查询一次，每次参与活动结束后只需保存一次。
#
# 例如：
# 个人竞技，组队竞技，帮会竞技：
# 上次参赛获得积分：ABCD
# 累计参赛获得积分：ABCD
#
# 武道大会，组队擂台，帮会擂台:
# 上次参赛获得名次：32强/16强/8强/4强/决赛/冠军 
# 获得最好参赛名次：32强/16强/8强/4强/决赛/冠军
#
# sm_param1和sm_param2可以根据比赛类型做不同的解释。比赛类型定义在csdefine中的MATCH_TYPE_***
# 各比赛的设计没有总体的规划，也没有良好的设计，同时此模块不考虑太多的扩展需要，可实现当前的比赛数据存储查询即可。


import BigWorld
from bwdebug import *
import csdefine
from Function import Functor

# 增加一条记录的sql语句
sqlCmdInsert = "insert into custom_RoleMatchRecord set sm_playerDBID = %i, sm_matchType = %i, sm_param1 = %i, sm_param2 = %i, sm_time = now();"
# 更新竞技类比赛信息的sql语句
sqlCmdUpdateCpt = "update custom_RoleMatchRecord set sm_param1 = %i, sm_param2 = sm_param2 + %i, sm_time = now() where sm_playerDBID = %i and sm_matchType = %i;"
# 更新擂台类比赛信息的sql语句
sqlCmdUpdateAba = "update custom_RoleMatchRecord set sm_param1 = %i, sm_param2 = if( %i < sm_param2, %i, sm_param2 ), sm_time = now() where sm_playerDBID = %i and sm_matchType = %i;"
# 查询比赛信息的sql语句
sqlCmdQuery = "select sm_matchType, sm_param1, sm_param2 from custom_RoleMatchRecord where sm_playerDBID = %i;"

cptMatchTypes = ( csdefine.MATCH_TYPE_PERSON_COMPETITION, csdefine.MATCH_TYPE_TEAM_COMPETITION, csdefine.MATCH_TYPE_TONG_COMPETITION )	# 竞技比赛定义类型集合
abaMatchTypes = ( csdefine.MATCH_TYPE_PERSON_ABA, csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_TONG_ABA )							# 擂台比赛定义类型集合

def getUpdateCmd( playerDBID, matchType, scoreOrRound ):	# 生成更新比赛日志的sql语句
	if matchType in cptMatchTypes:		# 竞技比赛
		return sqlCmdUpdateCpt % ( scoreOrRound, scoreOrRound, playerDBID, matchType )
	else:								# 其他是擂台比赛
		return sqlCmdUpdateAba % ( scoreOrRound, scoreOrRound, scoreOrRound, playerDBID, matchType )
		
def createTable():
	"""
	@sm_playerDBID : 玩家的dbid
	@sm_matchType : 活动类型
	@sm_param1 : 活动日志数据1，例如：上次参赛获得积分 或 上次参赛获得名次
	@sm_param2 : 活动日志数据2，例如：累计参赛获得积分 或 获得最好参赛名次
	@sm_time : 时间戳，更新比赛记录时此字段会被更新以标明记录的存在。避免更新的比赛数据如果和已经存在的数据一样时，
				记录不会被更改导致脚本会认为不存在此角色的记录而插入一条重复的纪录。
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
	
def update( playerDBID, matchType, scoreOrRound, playerBase = None ):	# 更新比赛数据
	sqlCmd = getUpdateCmd( playerDBID, matchType, scoreOrRound )
	BigWorld.executeRawDatabaseCommand( sqlCmd, Functor( updateCB, playerDBID, playerBase, matchType, scoreOrRound ) )
	
def updateCB( playerDBID, playerBase, matchType, scoreOrRound, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "update>>>( playerDBID:%i,matchType:%i,scoreOrRound:%i ):%s" % ( playerDBID, matchType, scoreOrRound, errstr ) )
		return
	if rows == 0:	# 没有相应的记录，那么建立此玩家的相关记录
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
		
def query( playerBase ):	# 玩家查询所有比赛日志
	sqlCmd = sqlCmdQuery % playerBase.databaseID
	BigWorld.executeRawDatabaseCommand( sqlCmd, Functor( queryCB, playerBase ) )
	
def queryCB( playerBase, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>playerDBID:%i:%s" % ( playerBase.databaseID, errstr ) )
		return
	if not result:
		DEBUG_MSG( "there is not result for player:%i." % playerBase.databaseID )
		return
	for matchType, param1, param2 in result:	# 目前每个玩家最多有6条
		playerBase.client.initMatchRecord( int( matchType ), int( param1 ), int( param2 ) )
