# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.8 2008-04-16 05:50:31 phw Exp $

"""
implement gameobject script class
2007/07/14: writen by huangyongwei
"""

import BigWorld
import random
from bwdebug import *

class GameObject( object ) :
	# 静态对像列表，key == object id, value == instance of GameObject
	objects_ = {}
	
	def __init__( self ):
		self.__propsDict = {}					# entity's property dictionary
		self.__entityType = ""					# entity's type defined in defs
		self.__className = ""					# only mark of the object

	@classmethod
	def getObject( SELF, className ) :
		"""
		get instance of the object via className
		@type				className : str
		@param				className : identifier of the object
		@rtype						  : GameObject
		@return						  : instance of the GameObject
		"""
		return SELF.objects_.get( className, None )

	@classmethod
	def register( SELF, className, instance ):
		"""
		注册一个实例到全局列表中
		@type				className : str
		@param				className : identifier of the object
		@param				instance  : 继承于GameObject的类实例
		@type				instance  : GameObject
		@rtype						  : GameObject
		@return						  : instance of the GameObject
		"""
		SELF.objects_[className] = instance
	
	@classmethod
	def hasObject( SELF, className ):
		"""
		判断指定的标识符已存在列表中
		@return: BOOL
		"""
		return className in SELF.objects_

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def className( self ) :
		return self.__className


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, call by GameObject::load().
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		self.setEntityProperty( "className", section["className"].asString )		# exclusive classfy mark

	# -------------------------------------------------
	def onCreateEntityInitialized_( self, entity ) :
		"""
		virtual method. Template method.
		you can override it, and initialize entity use your own datas
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getName( self ):
		"""
		virtual method.
		@rtype				: STRING
		@return				: the name of entity
		"""
		return self.__propsDict["uname"]

	def getEntityType( self ):
		"""
		get type of the entity
		@rtype				: str
		@return				: entity's type indicated in its config file's tag "EntityType"
		"""
		return self.__entityType

	def getClassName( self ) :
		"""
		get the exclusive classfy mark
		@rtype				: str
		@param				: exclusive classfy mark of the entity
		"""
		return self.__className

	# -------------------------------------------------
	def hasEntityProperty( self, name ) :
		"""
		indicate whether the entity contain property
		@rtype			name : str
		@param			name : proeprty name
		@rtype				 : bool
		@return				 : if the entity contain the property, it will return True
		"""
		return self.__propsDict.has_key( name )

	def getEntityProperty( self, name ) :
		"""
		get entity's property via property name
		@rtype			name : str
		@param			name : proeprty name
		@rtype				 : property's defination type
		@return				 : property value
		"""
		return self.__propsDict[name]

	def setEntityProperty( self, name, value ) :
		"""
		set entity's property value
		@rtype			name  : str
		@param			name  : property name
		@rtype			value : property's defination type
		@param			value : proeprty value
		@return				  : None
		"""
		self.__propsDict[name] = value

	def getEntityProperties( self ):
		"""
		get entity's property dictionary
		@rtype				: dict
		@return				: all properties
		"""
		return self.__propsDict

	# -------------------------------------------------
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from entity's coonfig file
		"""
		self.onLoadEntityProperties_( section )
		self.__entityType = section["EntityType"].asString
		self.__className = self.__propsDict["className"]

		self.registerSelf()		# 注册自身到全局

	def registerSelf( self ):
		"""
		virtual method.
		模版方式，用于被其它继承于此类的函数重载，以实现根据自身的情况执行不同的事情。
		默认把自己直接注册到全局列表中。
		在加载完成后，此接口会被底层自动调用。
		"""
		assert not self.hasObject( self.__className ), "the %s has already exist!" % ( self.__className )
		self.register( self.__className, self )

	# -------------------------------------------------
	def createLocalBase( self, param = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		@rtype						   : Entity
		@return						   : return a new entity
		"""
		# BigWorld.createBaseLocally() 的参数是：PyObject * args, PyObject * kwargs
		# 根据测试得出如果args里跟的是多个dict，那么在前面的dict的参数将优先于后面的dict的同名参数
		# 因此，合并属性的事情交由底层去做，这里不再判断
		args = []
		if param is not None:
			# 由于在某些情况下我们需要直接传进一个PyDataSection的属性集合，
			# 而如果改变当前函数的接口会使某些重载功能变得复杂，
			# 所以解决在最底层对传进来的“param”字典里的“PYDATASECTION”
			# 属性进行特例化处理。而“PYDATASECTION”会在param里出现，
			# 就表示“param”里其它的参数需要覆盖“PYDATASECTION”里的参数，
			# 所以在处理上我们会使“PYDATASECTION”这一个集合在“param”
			# 后面出现，以保证“param”里其它参数的优先级；
			args.append( param )
			if "PYDATASECTION" in param:
				args.append( param.pop( "PYDATASECTION" ) )
		
		args.append( self.__propsDict )
		entity = BigWorld.createBaseLocally( self.__entityType, *args )
		self.onCreateEntityInitialized_( entity )			# for initialize entity's property value which is generate temporarily
		return entity

	def createBaseAnywhere( self, param = None, callbackFunc = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		"""
		# BigWorld.createBaseAnywhere() 的参数是：PyObject * args, PyObject * kwargs
		# 根据测试得出如果args里跟的是多个dict，那么在前面的dict的参数将优先于后面的dict的同名参数
		# 因此，合并属性的事情交由底层去做，这里不再判断
		args = []
		if param is not None:
			# 由于在某些情况下我们需要直接传进一个PyDataSection的属性集合，
			# 而如果改变当前函数的接口会使某些重载功能变得复杂，
			# 所以解决在最底层对传进来的“param”字典里的“PYDATASECTION”
			# 属性进行特例化处理。而“PYDATASECTION”会在param里出现，
			# 就表示“param”里其它的参数需要覆盖“PYDATASECTION”里的参数，
			# 所以在处理上我们会使“PYDATASECTION”这一个集合在“param”
			# 后面出现，以保证“param”里其它参数的优先级；
			args.append( param )
			if "PYDATASECTION" in param:
				args.append( param.pop( "PYDATASECTION" ) )
		
		args.append( self.__propsDict )
		if callbackFunc is not None:
			args.append( callbackFunc )
		BigWorld.createBaseAnywhere( self.__entityType, *args )
