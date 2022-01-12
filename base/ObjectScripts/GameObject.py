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
	# ��̬�����б�key == object id, value == instance of GameObject
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
		ע��һ��ʵ����ȫ���б���
		@type				className : str
		@param				className : identifier of the object
		@param				instance  : �̳���GameObject����ʵ��
		@type				instance  : GameObject
		@rtype						  : GameObject
		@return						  : instance of the GameObject
		"""
		SELF.objects_[className] = instance
	
	@classmethod
	def hasObject( SELF, className ):
		"""
		�ж�ָ���ı�ʶ���Ѵ����б���
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

		self.registerSelf()		# ע������ȫ��

	def registerSelf( self ):
		"""
		virtual method.
		ģ�淽ʽ�����ڱ������̳��ڴ���ĺ������أ���ʵ�ָ�����������ִ�в�ͬ�����顣
		Ĭ�ϰ��Լ�ֱ��ע�ᵽȫ���б��С�
		�ڼ�����ɺ󣬴˽ӿڻᱻ�ײ��Զ����á�
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
		# BigWorld.createBaseLocally() �Ĳ����ǣ�PyObject * args, PyObject * kwargs
		# ���ݲ��Եó����args������Ƕ��dict����ô��ǰ���dict�Ĳ����������ں����dict��ͬ������
		# ��ˣ��ϲ����Ե����齻�ɵײ�ȥ�������ﲻ���ж�
		args = []
		if param is not None:
			# ������ĳЩ�����������Ҫֱ�Ӵ���һ��PyDataSection�����Լ��ϣ�
			# ������ı䵱ǰ�����Ľӿڻ�ʹĳЩ���ع��ܱ�ø��ӣ�
			# ���Խ������ײ�Դ������ġ�param���ֵ���ġ�PYDATASECTION��
			# ���Խ�����������������PYDATASECTION������param����֣�
			# �ͱ�ʾ��param���������Ĳ�����Ҫ���ǡ�PYDATASECTION����Ĳ�����
			# �����ڴ��������ǻ�ʹ��PYDATASECTION����һ�������ڡ�param��
			# ������֣��Ա�֤��param�����������������ȼ���
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
		# BigWorld.createBaseAnywhere() �Ĳ����ǣ�PyObject * args, PyObject * kwargs
		# ���ݲ��Եó����args������Ƕ��dict����ô��ǰ���dict�Ĳ����������ں����dict��ͬ������
		# ��ˣ��ϲ����Ե����齻�ɵײ�ȥ�������ﲻ���ж�
		args = []
		if param is not None:
			# ������ĳЩ�����������Ҫֱ�Ӵ���һ��PyDataSection�����Լ��ϣ�
			# ������ı䵱ǰ�����Ľӿڻ�ʹĳЩ���ع��ܱ�ø��ӣ�
			# ���Խ������ײ�Դ������ġ�param���ֵ���ġ�PYDATASECTION��
			# ���Խ�����������������PYDATASECTION������param����֣�
			# �ͱ�ʾ��param���������Ĳ�����Ҫ���ǡ�PYDATASECTION����Ĳ�����
			# �����ڴ��������ǻ�ʹ��PYDATASECTION����һ�������ڡ�param��
			# ������֣��Ա�֤��param�����������������ȼ���
			args.append( param )
			if "PYDATASECTION" in param:
				args.append( param.pop( "PYDATASECTION" ) )
		
		args.append( self.__propsDict )
		if callbackFunc is not None:
			args.append( callbackFunc )
		BigWorld.createBaseAnywhere( self.__entityType, *args )
