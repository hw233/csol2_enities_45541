# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.12 2008-04-16 05:54:28 phw Exp $

"""
"""
import BigWorld
import random
from bwdebug import *

class GameObject:
	"""
	"""
	# 静态对像列表，key == object id, value == instance of GameObject
	objects_ = {}
	def __init__( self ):
		"""
		初始化
		"""
		self.__propsDict = {}					# 存储用于初始化entity的属性表
		self.__entityType = ""					# 记录某entity创建时的类型（在defs/中定义的entity类型）
		self.className = ""						# NPC自身的唯一类型标识
	
	@classmethod
	def getObject( SELF, className ) :
		"""
		get instance of the object via className
		@type				className : str
		@param				className : identifier of the object
		@rtype						  : GameObject
		@return						  : instance of the GameObject
		"""
		obj = SELF.objects_.get( className, None )
		if not obj:
			ERROR_MSG( "game object '%s' not found." % (className) )
			printStackTrace()
		return obj

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

	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return self.__propsDict["uname"]

	def getEntityType( self ):
		"""
		获取相对应的entity type
		@return: STRING
		"""
		return self.__entityType

	def hasEntityProperty( self, name ) :
		"""
		是否存在某个属性

		@return: dict
		"""
		return self.__propsDict.has_key( name )

	def getEntityProperty( self, name ):
		"""
		取得全局的entity初始属性表

		@return: dict
		"""
		return self.__propsDict.get( name, None )

	def setEntityProperty( self, name, value ):
		"""
		设置entity创建时的初始化属性

		@param name: 属性名称，该名称必须存在于相应的Entity类型的.def文件中
		@type  name: STRING
		@param value: 与name对应的值，类型为与相应的.def中定义的name的取值类型
		"""
		self.__propsDict[name] = value

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		self.setEntityProperty( "className",	section["className"].asString )			# 唯一分类标识

	def load( self, section ):
		"""
		virtual method.
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		self.onLoadEntityProperties_( section )
		self.__entityType = section["EntityType"].asString
		self.className = self.__propsDict["className"]
		
		self.registerSelf()		# 注册自身到全局

	def registerSelf( self ):
		"""
		virtual method.
		模版方式，用于被其它继承于此类的函数重载，以实现根据自身的情况执行不同的事情。
		默认把自己直接注册到全局列表中。
		在加载完成后，此接口会被底层自动调用。
		"""
		assert not self.hasObject( self.className ), "the %s has already exist!" % ( self.className )
		self.register( self.className, self )

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		创建一个NPC实体在地图上
		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: entity的出生位置
		@type   position: VECTOR3
		@param direction: entity的出生方向
		@type  direction: VECTOR3
		@param      param: 该参数默认值为None，传给实体的数据
		@type    	param: dict
		@return:          一个新的NPC Entity
		@rtype:           Entity
		"""
		props = self.__propsDict.copy()
		if isinstance( param, dict ):
			props.update( param )
		entity = BigWorld.createEntity( self.__entityType, spaceID, position, direction, props )
		# 不在此处调用initEntity()方法，改为由entity在初始化时自己调用。
		# 这样可以解决"treatAllOtherEntitiesAsGhosts"参数为True时的一些问题。
		#self.initEntity( entity )		# 初始化entity的基础数据
		return entity

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		pass

# GameObject.py
