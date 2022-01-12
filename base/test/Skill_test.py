# -*- coding: gb18030 -*-
# $Id: Skill_test.py, added by dqh $

import BigWorld
from bwdebug import *
import csdefine
from Function import Functor
import Const

raceClasses = (csdefine.CLASS_FIGHTER,csdefine.CLASS_SWORDMAN,csdefine.CLASS_ARCHER,csdefine.CLASS_MAGE)		# 职业列表
#战士：323175001	csdefine.CLASS_FIGHTER
#剑客：323165001	csdefine.CLASS_SWORDMAN
#射手：323155001	csdefine.CLASS_ARCHER
#法师：323147001	csdefine.CLASS_MAGE
#RCMASK_CLASS							= 0x000000f0	# 职业掩码

# 取出对应职业的玩家
sqlCmdQuery = "select id from tbl_Role where sm_raceClass & 0x000000f0 = %i ;"

# 判断某角色是否已经存在指定技能
sqlCmdQueryID = " select sm_value from tbl_Role_attrSkillBox where parentID = %i and sm_value = %s;"

#往tbl_Role_attrSkillBox中插入一条数据
sqlCmdInsert = "insert into tbl_Role_attrSkillBox( parentID, sm_value ) values( %i, %s );"

def addThreeComboSkill():
	"""
	给老账号插入一个三连击技能
	"""
	for i in xrange(len(raceClasses) ):
		add( raceClasses[i] )
	
def add( type ):
	"""
	查询对应职业的玩家的ID，如果没有就返回该玩家的ID
	"""
	sqlCmd = sqlCmdQuery % type
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( queryCB, type ) )			# type 为csdefine里面定义的数据
	
def queryCB( type, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>type:%i" % ( type) )
		return
	print result
	if not result:
		DEBUG_MSG( "there is not result for type:%i." % type )
		return
	for id in result:
		skillID = Const.g_newBornGratuities[type]["skills"][3]			# 获取Type对应的skillID
		sqlCmd = sqlCmdQueryID % ( int(id[0]), skillID )
		BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( queryIDCB, type, int(id[0]), skillID ) )			# id为前一个查询返回的数据
		
def queryIDCB( type, id, skillID, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>type:%i" % ( id ) )
		return
	if result:
		DEBUG_MSG( "there is already exist:%i." % id )
		return
	skillID = Const.g_newBornGratuities[type]["skills"][3] # 获取Type对应的skillID
	sqlCmd = sqlCmdInsert % ( id, skillID )
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( inserCB, id, skillID ) )			# id为前一个查询返回的数据
		
def inserCB( id, skillID, result, rows, errstr  ):
	"""
	给玩家插入一个技能
	"""
	if errstr:
		ERROR_MSG( "insert>>>( id:%i,skillID:%s)" % ( id, skillID) )
		return
	print rows, "rows has been affected!"
