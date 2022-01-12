# -*- coding: gb18030 -*-
#
"""
帐号管理工具
删除、创建帐号/角色等集合。
"""

import BigWorld
from bwdebug import *
from Function import Functor

def escapeSQLStr( string ):
	"""
	转换sql关键字符
	"""
	s = []
	escapeStr = "\\'\";"
	for e in string:
		if e in escapeStr:
			s.append( "\\" )
		s.append( e )
	return "".join( s )

class EntityUtil( object ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.__locking = False	# 互斥锁
		# 创建entity完成后的回调; like as baseRef, databaseID and wasActive. 
		# see also __onBaseCreated()
		self.__callback = None
		
	def locked( self ):
		"""
		"""
		return self.__locking
		
	def __lock( self,  callback ):
		"""
		@return: bool
		"""
		if self.locked():
			return False
		self.__locking = True
		return True
		
	def __unlock( self ):
		"""
		"""
		self.__locking = False
		
	def createBaseFromDBID( self, entityType, dbid, callback = None ):
		"""
		virtual method.
		从数据库中创建一个entity

		@param entityType: STRING; like as "Role", "Account", etc.
		@return: bool
		"""
		if not self.__lock( callback ):
			return False
		self.__callback = callback
		BigWorld.createBaseLocallyFromDBID( entityType, dbid, self.__onBaseCreated )
		return True

	def createBaseFromDB( self, entityType, name, callback = None ):
		"""
		virtual method.
		从数据库中创建一个entity

		@param entityType: STRING; like as "Role", "Account", etc.
		@return: bool
		"""
		if not self.__lock( callback ):
			return False
		self.__callback = callback
		BigWorld.createBaseLocallyFromDB( entityType, name, self.__onBaseCreated )
		return True
		
	def __onBaseCreated( self, baseRef, databaseID, wasActive ):
		"""
		This is an optional callable object that will be called when operation completes.
		The callable object will be called with three arguments: baseRef, databaseID and wasActive. 
		If the operation was successful then baseRef will be a reference to the newly created Base entity, 
		databaseID will be the database ID of the entity and wasActive will indicate whether the entity was already active. 
		If wasActive is true, then baseRef is referring to a pre-existing Base entity and 
		may be a mailbox rather than a direct reference to a base entity. 
		If the operation failed, then baseRef will be None, 
		databaseID will be 0 and wasActive will be false. 
		The most common reason for failure is the that entity does not exist in the database 
		but intermittent failures like timeouts or unable to allocate IDs may also occur. 
		"""
		self.__unlock()
		
		callback = self.__callback
		self.__callback = None
		if callback is not None:
			callback( baseRef, databaseID, wasActive )

	def deleteBaseByDBID( self, entityType, dbid, callback ):
		"""
		This script function deletes the specified entry from the database, 
		if it is not already checked out. If it is checked out, 
		then the result handler will be called with the mailbox of the currently checked out entity. 

		Parameters: 
		entityType	entityType is a string that specificies the type of the entity to be deleted.  
		dbid		Specifies the dbid of the entity to delete.  
		callback	callback is a callable object (e.g. a function) that takes one argument. 
					If deletion is successful, the callback is called with the value True, 
					if it is unsuccessful because the specified entry is currently checked out, 
					it is called with the mailbox of that base entity, 
					and if it is unsuccessful for any other reason (e.g. specified entry does not exist) then it is called with the value False.  
		"""
		BigWorld.deleteBaseByDBID( entityType, dbid, callback )

class EntityDeleter( EntityUtil ):
	"""
	角色删除模块
	注意：此行为必须在该角色未登录游戏时才有意义，否则无法从数据库中删除角色。
	"""
	def deleteByDBID( self, entityType, dbid ):
		"""
		"""
		self.deleteBaseByDBID( entityType, dbid, Functor( self.onDeleteByDBID, entityType, dbid ) )
		
	def onDeleteByDBID( self, entityType, databaseID, state ):
		"""
		virtual method.
		see also: EntityUtil.deleteBaseByDBID()
		"""
		if state != True:
			if state == False:
				ERROR_MSG( "entity %i(type = %s) remove fault, maybe it not exist in database." % ( databaseID, entityType ) )
			else:
				ERROR_MSG( "entity %i(type = %s) remove fault, because it check out now." % ( databaseID, entityType ) )
			return
		else:
			INFO_MSG( "entity %i(type = %s) remove success." % ( databaseID, entityType ) )

class AccountRolesDeleter( EntityUtil ):
	"""
	删除某一个帐号下所有的角色；
	注意：此行为必须在该帐号及帐号下的角色未登录游戏时才有意义，否则无法从数据库中完全删除。
	"""

	class Deleter( EntityDeleter ):
		def __init__( self, items, breakOnFault = False, callback = None ):
			"""
			@param items: 要删除的角色列表；like as ( (entityType, dbid, name), ... )
			@param callback: 完成回调，有一个参数“success”，表示是否所有角色都被删除
			"""
			self.items = list( items )
			self.breakOnFault = breakOnFault
			self.callbackFunc = callback
			
		def __call__( self ):
			"""
			virtual method.
			"""
			if len( self.items ) == 0:
				INFO_MSG( "Finished to delete entity by database id." )
				self.__callback( True )
				return
			self.__tmpType, self.__tmpDBID, self.__tmpName = self.items.pop( 0 )
			INFO_MSG( "Deleting '%s' entity '%s' by database %i." % ( self.__tmpType, self.__tmpName, self.__tmpDBID ) )
			self.deleteByDBID( self.__tmpType, self.__tmpDBID )
			
		def onDeleteByDBID( self, entityType, databaseID, state ):
			"""
			virtual method.
			see also: EntityUtil.deleteBaseByDBID()
			"""
			EntityDeleter.onDeleteByDBID( self, entityType, databaseID, state )
			if state != True and self.breakOnFault:
				self.__callback( False )
				return
			self.__call__()
		
		def __callback( self, success ):
			"""
			"""
			callbackFunc = self.callbackFunc
			self.callbackFunc = None	# 这个一定要做，以避免交叉引用
			if callable( callbackFunc ):
				callbackFunc( success )
		# end of class: Deleter
	
	def __init__( self ):
		self.accountName = ""
		self.accountDBID = 0
		
	def do( self, accountName ):
		"""
		删除指定帐号下所有的角色。
		"""
		self.accountName = accountName
		query = "select id from tbl_Account where sm_playerName = '%s';" % BigWorld.escape_string( accountName )
		BigWorld.executeRawDatabaseCommand( query, self.__onQueryAccountDBID )
		
	def __onQueryAccountDBID( self, resultSet, rows, errstr ):
		"""
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
			
		if len( resultSet ) == 0:
			INFO_MSG( "account '%s' not found." % ( self.accountName, self.accountDBID ) )
		else:
			self.__deleteByDBID( long( resultSet[0][0] ) )
		
	def __deleteByDBID( self, databaseID ):
		"""
		为了有更详细的记录，有些地方必须记录account name，因此把此接口置为私有接口，以免误用。
		"""
		self.accountDBID = databaseID
		query = "select a.id, r.id, r.sm_playerName from tbl_Account as a, tbl_Role as r where \
					a.id = '%i' and a.id = r.sm_parentDBID;" % self.accountDBID
		BigWorld.executeRawDatabaseCommand( query, self.onQueryRole_ )

	def onQueryRole_( self, resultSet, rows, errstr ):
		"""
		The object to call back (e.g. a function) with the result of the command execution.
		The callback will be called with 3 parameters: result set, number of affected rows and error string.

		@param resultSet: format: [ [ accountDBID, roleDBID, roleName ], ... ]
						list of list of string like as [ [ field1, field2, ... ], ... ];
						The result set parameter is a list of rows.
						Each row is a list of strings containing field values.
						The XML database will always return a result set with 1 row and 1 column containing the return code of the command.
						The result set will be None for commands to do not return a result set e.g. DELETE,
						or if there was an error in executing the command.
		@param rows:	The number of a affected rows parameter is a number indicating the number of rows affected by the command.
						This parameter is only relevant for commands to do not return a result set e.g. DELETE.
						This parameter is None for commands that do return a result set or if there was and error in executing the command.
		@param errstr:	The error string parameter is a string describing the error that occurred if there was an error in executing the command.
						This parameter is None if there was no error in executing the command.
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
			
		INFO_MSG( "Account-Role result set -->", resultSet )
		roleList = []
		if len( resultSet ) == 0:
			INFO_MSG( "account '%s(%i)' has no any entity." % ( self.accountName, self.accountDBID ) )
		else:
			# resultSet format: [ [ accountDBID, roleDBID, roleName ], ... ]
			roleList = [( "Role", long( e[1] ), e[2] ) for e in resultSet]					# 汇总所有角色用于登录、删除操作时认证
		
		instance = AccountRolesDeleter.Deleter( roleList, True, None )
		instance()



class AccountDeleter( AccountRolesDeleter ):
	"""
	删除某一个帐号
	注意：此行为必须在该帐号及帐号下的角色未登录游戏时才有意义，否则无法从数据库中完全删除角色。
	"""
	def __init__( self ):
		AccountRolesDeleter.__init__( self )
		
	def onQueryRole_( self, resultSet, rows, errstr ):
		"""
		The object to call back (e.g. a function) with the result of the command execution.
		The callback will be called with 3 parameters: result set, number of affected rows and error string.

		@param resultSet: format: [ [ accountDBID, roleDBID, roleName ], ... ]
						The result set parameter is a list of rows.
						Each row is a list of strings containing field values.
						The XML database will always return a result set with 1 row and 1 column containing the return code of the command.
						The result set will be None for commands to do not return a result set e.g. DELETE,
						or if there was an error in executing the command.
		@param rows:	The number of a affected rows parameter is a number indicating the number of rows affected by the command.
						This parameter is only relevant for commands to do not return a result set e.g. DELETE.
						This parameter is None for commands that do return a result set or if there was and error in executing the command.
		@param errstr:	The error string parameter is a string describing the error that occurred if there was an error in executing the command.
						This parameter is None if there was no error in executing the command.
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
			
		INFO_MSG( "Account-Role result set -->", resultSet )
		roleList = []
		if len( resultSet ) == 0:
			INFO_MSG( "account '%s(%i)' has no any entity." % ( self.accountName, self.accountDBID ) )
		else:
			# resultSet format: [ [ accountDBID, roleDBID, roleName ], ... ]
			roleList = [( "Role", long( e[1] ), e[2] ) for e in resultSet]					# 汇总所有角色用于登录、删除操作时认证
		
		roleList.insert( 0, ( "Account", self.accountDBID, self.accountName ) )	
		instance = AccountRolesDeleter.Deleter( roleList, True, self.__onRoleDeleted )
		instance()

	def __onRoleDeleted( self, success ):
		"""
		"""
		if success:
			INFO_MSG( "removing '%s' from bigworldLogOnMapping..." % self.accountName )
			sql = 'delete from bigworldLogOnMapping where logOnName = "%s";' % BigWorld.escape_string( self.accountName )
			BigWorld.executeRawDatabaseCommand( sql, self.__onAccountDeletedFromMapping )
		else:
			ERROR_MSG( "remove account '%s' fault. some Role entity maybe remove fault." % BigWorld.escape_string( self.accountName ) )
			
	def __onAccountDeletedFromMapping( self, resultSet, rows, errstr ):
		"""
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
			
		INFO_MSG( "account '%s' is removed from bigworldLogOnMapping." % self.accountName )



class AccountsDeleter( EntityUtil ):
	"""
	批量删除帐号工具；
	注意：此行为必须在该帐号及帐号下的角色未登录游戏时才有意义，否则无法从数据库中完全删除。
	"""
	def delete( self, nameExpression, limit = 10 ):
		"""
		@param nameExpression: 需要批量删除的帐号表达式，如："test%"
		@param limit: 最多删除个数。这个参数的存在是为了避免因为一次删除太多导致服务器被阻塞而引起服务器崩溃所设。
		"""
		self.accountExpression = nameExpression
		query = "select sm_playerName from tbl_Account where sm_playerName like '%s' limit %i;" % ( BigWorld.escape_string( nameExpression ), limit )
		BigWorld.executeRawDatabaseCommand( query, self.__onQuery )

	def __onQuery( self, resultSet, rows, errstr ):
		"""
		The object to call back (e.g. a function) with the result of the command execution.
		The callback will be called with 3 parameters: result set, number of affected rows and error string.

		@param resultSet:	list of list of string like as [ [ field1, field2, ... ], ... ];
						The result set parameter is a list of rows.
						Each row is a list of strings containing field values.
						The XML database will always return a result set with 1 row and 1 column containing the return code of the command.
						The result set will be None for commands to do not return a result set e.g. DELETE,
						or if there was an error in executing the command.
		@param rows:	The number of a affected rows parameter is a number indicating the number of rows affected by the command.
						This parameter is only relevant for commands to do not return a result set e.g. DELETE.
						This parameter is None for commands that do return a result set or if there was and error in executing the command.
		@param errstr:	The error string parameter is a string describing the error that occurred if there was an error in executing the command.
						This parameter is None if there was no error in executing the command.
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
			
		INFO_MSG( "Account like '%s' result set -->" % self.accountExpression, resultSet )
		if len( resultSet ) == 0:
			INFO_MSG( "no delete any accounts." )
			return
			
		roleList = [ e[0] for e in resultSet ]		# resultSet format: [ [ accountName ], ... ]
		for e in roleList:
			instance = AccountDeleter()
			instance.deleteByName( e )



class AccountCreator( EntityUtil ):
	"""
	创建新帐号
	"""
	def __init__( self, name, password, isMd5Pwd = False ):
		"""
		@param name: 帐号名
		@param password: 密码
		@param isMd5Pwd: 表示password是否为md5字符串的还是原始字符串的
		"""
		self.name = BigWorld.escape_string( name )
		if isMd5Pwd:
			self.password = '"%s"' % password
		else:
			self.password = 'md5( "%s" )' % password
		self.logonMappingSQL = 'insert into bigworldLogOnMapping ( `logOnName`, `password`, `typeID`, `recordName` ) select "%s", %s, typeID, "%s" from bigworldEntityTypes where name = "Account";' % ( self.name, self.password, self.name )
		
	def __call__( self ):
		"""
		创建帐号
		"""
		# 创建entity
		entity = BigWorld.createBaseLocally( "Account", { "playerName" : self.name } )
		entity.writeToDB( self.__onWriteEntityToDBOver )

	def __onWriteEntityToDBOver( self, success, entity ):
		"""
		callback of writeToDB()
		see also: Base::entity.writeToDB()
		"""
		if success:
			INFO_MSG( "wrote entity '%s' to db ok." % BigWorld.escape_string( self.name ) )
			BigWorld.executeRawDatabaseCommand( self.logonMappingSQL, self.__onWriteAccountInfoOver )
		else:
			ERROR_MSG( "wrote entity '%s' to db fault." % self.name )
		
		# however, we also destroy the entity.
		entity.destroy( writeToDB = False )
		
	def __onWriteAccountInfoOver( self, resultSet, rows, errstr ):
		"""
		see also: BigWorld.executeRawDatabaseCommand()
		"""
		if errstr:
			ERROR_MSG( "wrote account info to talbe bigworldLogOnMapping error.", errstr )
		else:
			INFO_MSG( "wrote account info to talbe bigworldLogOnMapping ok." )
			INFO_MSG( "account '%s' created ok." % self.name )
		
# AccountUtil.py
