# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
from Function import Functor
import Const

# 将不在当前可选PK模式中的模式更新为某一默认值
sqlCmdUpdate = "update tbl_Role set sm_pkMode = %i where sm_pkMode not in %s;"

def updateRolePKMode( defaultMode, modes ):
	"""
	修改玩家的PK模式为某一个默认值
	defaultMode 默认值
	modes 现在界面上使用的PK模式，在csdefine中定义，参数格式可以填写为元组,如：(5,6,7)
	eg:updateRolePKMode( 5, ( 5, 6, 7 ) )
	"""
	sqlCmd = sqlCmdUpdate % ( int(defaultMode), tuple( modes) )
	BigWorld.executeRawDatabaseCommand(  sqlCmd, Functor( updateCB, defaultMode, modes ) )

def updateCB( defaultMode, modes, result, rows, errstr ):
	"""
	更新回调
	"""
	if errstr:
		ERROR_MSG( "update>>> defaultMode:%i error " % defaultMode )
		return
	INFO_MSG( "Update role PK mode whick is not in %s to defaultMode %i, %i rows has been affected! " % ( modes, defaultMode, rows ) )