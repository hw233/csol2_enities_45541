# -*- coding: gb18030 -*-
#
# $Id: GameObjectFactory.py,v 1.6 2008-05-17 11:51:07 huangyongwei Exp $

"""
load game object config files

2007/12/15 : tidy up by huangyongwei
"""

import sys
import Language
import Function
from bwdebug import *
from GameObject import GameObject
from SmartImport import smartImport


class GameObjectFactory( GameObject ):
	__inst = None
	sections = []
	
	def __init__( self ):
		assert GameObjectFactory.__inst is None, "instance already existed."


	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = GameObjectFactory()
		return SELF.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def _createObject( self, scriptName, sect ) :
		try:
			ObjClass = smartImport( "ObjectScripts." + scriptName + ":" + scriptName )
		except ImportError, err :
			ERROR_MSG( "loading game object '%s'(script: '%s'), its cell map class is not exist!" % ( sect.readString( "className" ), scriptName ) )
			sys.excepthook(*sys.exc_info())
			return None

		obj = ObjClass()
		try :
			obj.load( sect )
		except Exception, err:
			ERROR_MSG( "loading game object '%s' error: %s" % ( sect.readString( "className" ), err ) )
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
			ERROR_MSG( "gameObject config file is not exist : '%s'." % config )
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


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, filesPath ) :
		"""
		load the entities' config files
		@type				filesPath : string
		@param				filesPath : directory of the xml config files
		@return						  : None
		"""
		sect = Language.openConfigSection( filesPath )
		if sect is None : raise SystemError, "can't load '%s'. " % filesPath
		paths = [e for e in sect.readStrings( "path" )]				# get all config paths
		Language.purgeConfig( filesPath )
		files = Language.searchConfigFile( paths, ".xml" )							# get all config files
		bigfiles = []	#这类文件是很大的文件， 分出来主要是这类文件在服务器启动时不进行初始化
		if sect.has_key( "files" ):
			bigfiles =  sect["files"].readStrings( "path" )

		count1 = count2 = 0														# the number of success and fail of loading
		for fileName in files :
			sCount, fCount = self.__buildObject( fileName, True )						# 成功读取数量，失败读取数量
			count2 += fCount
			count1 += sCount
		for fileName in bigfiles :
			self.__buildObject( fileName, False )			

		INFO_MSG( "load game objects %d fail, %d success!" % ( count2, count1 ) )

	# ---------------------------------------
	def createEntity( self, className, spaceID, position, direction, param = None ) :
		"""
		create an entity in the wirld
		@type				className : str
		@param				className : identifier of the object
		@type				spaceID	  : INT32
		@param				spaceID	  : space the entity loacte in
		@type				position  : Vector3
		@param				position  : position the entity in the world
		@type				direction : Vector3
		@param				direction : dorection the entity in the world
		@type				param	  : dict
		@param				param	  : properties dict
		@rtype						  : Entity
		@return						  : an new entity
		"""
		return self.getObject( className ).createEntity( spaceID, position, direction, param )

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
					if len( scriptName ) == 0:
						ERROR_MSG( "entity type '%s' has no script name to create new instance." % className )
						return None
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
		
# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
g_objFactory = GameObjectFactory.instance()
