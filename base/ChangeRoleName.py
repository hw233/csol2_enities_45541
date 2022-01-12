# -*- coding: gb18030 -*-


"""
合服时玩家名字如和其他玩家有冲突则按一定规则修改玩家名字，
玩家改名功能仅限于按此规则命名的玩家使用，同时玩家创建角色时不允许玩家如此命名。
如此，玩家改名功能仅能被因合服被系统更改名字的玩家使用。
"""

from bwdebug import *
import BigWorld
import csstatus
from Function import Functor


def changeRoleNameCB( entity, roleDBID, escapeOldName, escapeNewName, newName, result, rows, errstr ):
	if errstr:	# 该名称已被使用,请换一个名称。
		ERROR_MSG( "account entity( %s ) change role( %i ) name( %s ) to ( %s ) failed:%s." % ( entity.getName(), roleDBID, escapeOldName, newName, errstr ) )
		if not entity.isDestroyed and hasattr( entity, "client" ):
			entity.statusMessage( csstatus.ACCOUNT_STATE_NAME_EXIST )
	else:
		if not entity.isDestroyed and hasattr( entity, "client" ):
			entity.changeRoleNameSuccess( roleDBID, newName )
		INFO_MSG( "account entity( %s ) change role( %i ) name( %s ) to ( %s ) succeeded." % ( entity.getName(), roleDBID, escapeOldName, newName ) )

def changeName( entity, roleDBID, oldName, newName ):
	"""
	改变名字
	"""
	INFO_MSG( "account( %i ) change player( %i )'s name( %s ) to a newName( %s )" % ( entity.databaseID, roleDBID, oldName, newName ) )
	escapeOldName = BigWorld.escape_string( oldName )
	escapeNewName = BigWorld.escape_string( newName )
	procedureString = "call CHANGEROLENAME( \'%s\', \'%s\' )" % ( escapeOldName, escapeNewName )
	BigWorld.executeRawDatabaseCommand( procedureString, Functor( changeRoleNameCB, entity, roleDBID, escapeOldName, escapeNewName, newName ) )
