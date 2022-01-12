# -*- coding: gb18030 -*-
#
# $Id: GameObjectFactory.py,v 1.12 2008-05-17 11:50:47 huangyongwei Exp $

"""
load all npcs need to local in base
2007/07/14: writen by huangyongwei
"""

import sys
import Language
from bwdebug import *
from GameObject import GameObject
from SmartImport import smartImport
import Function

class GameObjectFactory( GameObject ):
	__instance = None
	sections = []

	def __init__( self ) :
		assert GameObjectFactory.__instance is None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def instance( SELF ) :
		if SELF.__instance is None :
			SELF.__instance = GameObjectFactory()
		return SELF.__instance

	# -------------------------------------------------
	def __getObjectFiles( self, filesPath ) :
		sect = Language.openConfigSection( filesPath )
		if sect is None : raise SystemError, "can't load %s " % filesPath
		paths = [e for e in sect.readStrings( "path" )]				# get all config paths
		Language.purgeConfig( filesPath )
		files = Language.searchConfigFile( paths, ".xml" )							# get all config files
		bigfiles = []	#这类文件是很大的文件， 分出来主要是这类文件在服务器启动时不进行初始化
		if sect.has_key( "files" ):
			bigfiles =  sect["files"].readStrings( "path" )
		return files, bigfiles				# get all game object config files which their extension is ".xml"

	def _createObject( self, scriptName, sect ) :
		if scriptName.strip() == "" :
			ERROR_MSG( "script of entity '%s' is not exist!" % sect.readString( "className" ) )
			return None
		try:
			ObjClass = smartImport( "ObjectScripts." + scriptName + ":" + scriptName )
		except ImportError, err :
			#ERROR_MSG( "loading game object %s(%s), its cell map class is not exist!" % ( sect.readString( "className" ), scriptName ) )
			# 不输出此日志，我们允许baseapp不加载不存在的entity
			return None

		obj = ObjClass()
		try :
			obj.load( sect )
		except Exception, err:
			ERROR_MSG( "loading game object %s error: %s" % ( sect.readString( "className" ), err ) )
			sys.excepthook(*sys.exc_info())

		return obj

	def __buildObject( self, config, isInit ) :
		"""
		@retnrun: 成功读取数量，失败读取数量
		@rtype: INT,INT
		"""
		obj = None
		section = Language.openConfigSection( config )
		if section is None :
			ERROR_MSG( "gameObject config file is not exist : %s" % config )
			return 0, 1
		if not isInit:
			self.sections.append( section )
			return 0, 1# 修改为动态加载方式

		sCount = fCount = 0
		if section.childName( 0 ) == "row":
			for index in xrange( len( section ) ):
				childSection = section.child( index )
				scriptName = childSection.readString( "script" )
				obj = self._createObject( scriptName, childSection )
				if obj:
					sCount += 1
				else:
					fCount += 1
		else:
			scriptName = section.readString( "script" )
			obj = self._createObject( scriptName, section )
			if obj:
				sCount += 1
			else:
				fCount += 1
		return sCount, fCount

	@classmethod
	def getObject( SELF, className ) :
		"""
		get instance of the object via className
		@type				className : str
		@param				className : identifier of the object
		@rtype						  : GameObject
		@return						  : instance of the GameObject
		"""
		if not className in SELF.objects_:
			for section in SELF.sections:
				if section.has_key( className ):
					childSection = section[ className ]
					scriptName = childSection.readString( "script" )
					return GameObjectFactory.instance()._createObject( scriptName, childSection )
		return GameObject.getObject( className )

	@classmethod
	def hasObject( SELF, className ):
		"""
		判断指定的标识符已存在列表中
		@return: BOOL
		"""
		hasObject = GameObject.hasObject( className )
		if hasObject:
			return hasObject

		for section in SELF.sections:
			if section.has_key( className ):
				return True
		return False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, filePath ) :
		"""
		load all npcs from config file
		@type			filePath : str
		@param			filePath : file indicates all game object config files path
		"""
		files, bigfiles = self.__getObjectFiles( filePath )
		succCount = errorCount = 0
		for fileName in files :
			sCount, fCount = self.__buildObject( fileName, True )						# 成功读取数量，失败读取数量
			errorCount += fCount
			succCount += sCount
		for fileName in bigfiles :
			self.__buildObject( fileName, False )
		INFO_MSG( "Load global GameObject config from %s. %i success, %i fail." % ( filePath, succCount, errorCount ) )

	# -------------------------------------------------
	def createLocalBase( self, className, param = None ) :
		"""
		create an entity locate in the map
		@type				className : str
		@param				className : the entity's class name
		@type				param	  : dict
		@param				param	  : property dictionary
		@rtype						  : Entity
		@return						  : return a new entity
		"""
		obj = self.getObject( className )
		if obj is None:
			ERROR_MSG( "object which its className is %s is not exist" % className )
			return None
		return obj.createLocalBase( param )

	# -------------------------------------------------
	def createBaseAnywhere( self, className, param = None, callback = None ) :
		"""
		create an entity locate in the map
		@type				className : str
		@param				className : the entity's class name
		@type				param	  : dict
		@param				param	  : property dictionary
		@rtype						  : Entity
		@return						  : return a new entity
		"""
		obj = self.getObject( className )
		if obj is None:
			ERROR_MSG( "object which its className is %s is not exist" % className )
			return None
		return obj.createBaseAnywhere( param, callback )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
g_objFactory = GameObjectFactory.instance()
