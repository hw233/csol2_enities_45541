# -*- coding: gb18030 -*-
# $Id: Skill_test.py, added by dqh $

import BigWorld
from bwdebug import *
import csdefine
from Function import Functor
import Const

raceClasses = (csdefine.CLASS_FIGHTER,csdefine.CLASS_SWORDMAN,csdefine.CLASS_ARCHER,csdefine.CLASS_MAGE)		# ְҵ�б�
#սʿ��323175001	csdefine.CLASS_FIGHTER
#���ͣ�323165001	csdefine.CLASS_SWORDMAN
#���֣�323155001	csdefine.CLASS_ARCHER
#��ʦ��323147001	csdefine.CLASS_MAGE
#RCMASK_CLASS							= 0x000000f0	# ְҵ����

# ȡ����Ӧְҵ�����
sqlCmdQuery = "select id from tbl_Role where sm_raceClass & 0x000000f0 = %i ;"

# �ж�ĳ��ɫ�Ƿ��Ѿ�����ָ������
sqlCmdQueryID = " select sm_value from tbl_Role_attrSkillBox where parentID = %i and sm_value = %s;"

#��tbl_Role_attrSkillBox�в���һ������
sqlCmdInsert = "insert into tbl_Role_attrSkillBox( parentID, sm_value ) values( %i, %s );"

def addThreeComboSkill():
	"""
	�����˺Ų���һ������������
	"""
	for i in xrange(len(raceClasses) ):
		add( raceClasses[i] )
	
def add( type ):
	"""
	��ѯ��Ӧְҵ����ҵ�ID�����û�оͷ��ظ���ҵ�ID
	"""
	sqlCmd = sqlCmdQuery % type
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( queryCB, type ) )			# type Ϊcsdefine���涨�������
	
def queryCB( type, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>type:%i" % ( type) )
		return
	print result
	if not result:
		DEBUG_MSG( "there is not result for type:%i." % type )
		return
	for id in result:
		skillID = Const.g_newBornGratuities[type]["skills"][3]			# ��ȡType��Ӧ��skillID
		sqlCmd = sqlCmdQueryID % ( int(id[0]), skillID )
		BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( queryIDCB, type, int(id[0]), skillID ) )			# idΪǰһ����ѯ���ص�����
		
def queryIDCB( type, id, skillID, result, rows, errstr ):
	if errstr:
		ERROR_MSG( "query>>>type:%i" % ( id ) )
		return
	if result:
		DEBUG_MSG( "there is already exist:%i." % id )
		return
	skillID = Const.g_newBornGratuities[type]["skills"][3] # ��ȡType��Ӧ��skillID
	sqlCmd = sqlCmdInsert % ( id, skillID )
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( inserCB, id, skillID ) )			# idΪǰһ����ѯ���ص�����
		
def inserCB( id, skillID, result, rows, errstr  ):
	"""
	����Ҳ���һ������
	"""
	if errstr:
		ERROR_MSG( "insert>>>( id:%i,skillID:%s)" % ( id, skillID) )
		return
	print rows, "rows has been affected!"
