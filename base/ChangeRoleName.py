# -*- coding: gb18030 -*-


"""
�Ϸ�ʱ������������������г�ͻ��һ�������޸�������֣�
��Ҹ������ܽ����ڰ��˹������������ʹ�ã�ͬʱ��Ҵ�����ɫʱ������������������
��ˣ���Ҹ������ܽ��ܱ���Ϸ���ϵͳ�������ֵ����ʹ�á�
"""

from bwdebug import *
import BigWorld
import csstatus
from Function import Functor


def changeRoleNameCB( entity, roleDBID, escapeOldName, escapeNewName, newName, result, rows, errstr ):
	if errstr:	# �������ѱ�ʹ��,�뻻һ�����ơ�
		ERROR_MSG( "account entity( %s ) change role( %i ) name( %s ) to ( %s ) failed:%s." % ( entity.getName(), roleDBID, escapeOldName, newName, errstr ) )
		if not entity.isDestroyed and hasattr( entity, "client" ):
			entity.statusMessage( csstatus.ACCOUNT_STATE_NAME_EXIST )
	else:
		if not entity.isDestroyed and hasattr( entity, "client" ):
			entity.changeRoleNameSuccess( roleDBID, newName )
		INFO_MSG( "account entity( %s ) change role( %i ) name( %s ) to ( %s ) succeeded." % ( entity.getName(), roleDBID, escapeOldName, newName ) )

def changeName( entity, roleDBID, oldName, newName ):
	"""
	�ı�����
	"""
	INFO_MSG( "account( %i ) change player( %i )'s name( %s ) to a newName( %s )" % ( entity.databaseID, roleDBID, oldName, newName ) )
	escapeOldName = BigWorld.escape_string( oldName )
	escapeNewName = BigWorld.escape_string( newName )
	procedureString = "call CHANGEROLENAME( \'%s\', \'%s\' )" % ( escapeOldName, escapeNewName )
	BigWorld.executeRawDatabaseCommand( procedureString, Functor( changeRoleNameCB, entity, roleDBID, escapeOldName, escapeNewName, newName ) )
