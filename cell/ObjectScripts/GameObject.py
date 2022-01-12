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
	# ��̬�����б�key == object id, value == instance of GameObject
	objects_ = {}
	def __init__( self ):
		"""
		��ʼ��
		"""
		self.__propsDict = {}					# �洢���ڳ�ʼ��entity�����Ա�
		self.__entityType = ""					# ��¼ĳentity����ʱ�����ͣ���defs/�ж����entity���ͣ�
		self.className = ""						# NPC�����Ψһ���ͱ�ʶ
	
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

	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return self.__propsDict["uname"]

	def getEntityType( self ):
		"""
		��ȡ���Ӧ��entity type
		@return: STRING
		"""
		return self.__entityType

	def hasEntityProperty( self, name ) :
		"""
		�Ƿ����ĳ������

		@return: dict
		"""
		return self.__propsDict.has_key( name )

	def getEntityProperty( self, name ):
		"""
		ȡ��ȫ�ֵ�entity��ʼ���Ա�

		@return: dict
		"""
		return self.__propsDict.get( name, None )

	def setEntityProperty( self, name, value ):
		"""
		����entity����ʱ�ĳ�ʼ������

		@param name: �������ƣ������Ʊ����������Ӧ��Entity���͵�.def�ļ���
		@type  name: STRING
		@param value: ��name��Ӧ��ֵ������Ϊ����Ӧ��.def�ж����name��ȡֵ����
		"""
		self.__propsDict[name] = value

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		self.setEntityProperty( "className",	section["className"].asString )			# Ψһ�����ʶ

	def load( self, section ):
		"""
		virtual method.
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		self.onLoadEntityProperties_( section )
		self.__entityType = section["EntityType"].asString
		self.className = self.__propsDict["className"]
		
		self.registerSelf()		# ע������ȫ��

	def registerSelf( self ):
		"""
		virtual method.
		ģ�淽ʽ�����ڱ������̳��ڴ���ĺ������أ���ʵ�ָ�����������ִ�в�ͬ�����顣
		Ĭ�ϰ��Լ�ֱ��ע�ᵽȫ���б��С�
		�ڼ�����ɺ󣬴˽ӿڻᱻ�ײ��Զ����á�
		"""
		assert not self.hasObject( self.className ), "the %s has already exist!" % ( self.className )
		self.register( self.className, self )

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		����һ��NPCʵ���ڵ�ͼ��
		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: entity�ĳ���λ��
		@type   position: VECTOR3
		@param direction: entity�ĳ�������
		@type  direction: VECTOR3
		@param      param: �ò���Ĭ��ֵΪNone������ʵ�������
		@type    	param: dict
		@return:          һ���µ�NPC Entity
		@rtype:           Entity
		"""
		props = self.__propsDict.copy()
		if isinstance( param, dict ):
			props.update( param )
		entity = BigWorld.createEntity( self.__entityType, spaceID, position, direction, props )
		# ���ڴ˴�����initEntity()��������Ϊ��entity�ڳ�ʼ��ʱ�Լ����á�
		# �������Խ��"treatAllOtherEntitiesAsGhosts"����ΪTrueʱ��һЩ���⡣
		#self.initEntity( entity )		# ��ʼ��entity�Ļ�������
		return entity

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		pass

# GameObject.py
