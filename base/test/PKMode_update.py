# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
from Function import Functor
import Const

# �����ڵ�ǰ��ѡPKģʽ�е�ģʽ����ΪĳһĬ��ֵ
sqlCmdUpdate = "update tbl_Role set sm_pkMode = %i where sm_pkMode not in %s;"

def updateRolePKMode( defaultMode, modes ):
	"""
	�޸���ҵ�PKģʽΪĳһ��Ĭ��ֵ
	defaultMode Ĭ��ֵ
	modes ���ڽ�����ʹ�õ�PKģʽ����csdefine�ж��壬������ʽ������дΪԪ��,�磺(5,6,7)
	eg:updateRolePKMode( 5, ( 5, 6, 7 ) )
	"""
	sqlCmd = sqlCmdUpdate % ( int(defaultMode), tuple( modes) )
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( updateCB, defaultMode, modes ) )

def updateCB( defaultMode, modes, result, rows, errstr ):
	"""
	���»ص�
	"""
	if errstr:
		ERROR_MSG( "update>>> defaultMode:%i error " % defaultMode )
		return
	INFO_MSG( "Update role PK mode whick is not in %s to defaultMode %i, %i rows has been affected! " % ( modes, defaultMode, rows ) )