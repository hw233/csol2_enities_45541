# -*- coding: utf-8 -*-
#
# $Id: SkillTargetObjImpl.py 690 2009-06-11 02:58:18Z qilan $

"""
�����ߣ������C++�Ƕ������������ǿ������������Ϊһ���������CReceiver��
						�ö�������þ��ǳ������ʩ����˵����Ҫ��һЩ�ӿڣ�Ȼ����һ�п��ܵĽ����߶�
						�̳���������λ�ã�CReceiverPosition����entity��CReceiverEntity����
						���������Ʒ��CReceiverItem���ȣ����Ը��ݳ���Ľӿ�ʵ���Լ���ʵ�֣�
						����������ʩչʱ����ͳһ�ӿڣ��Ҳ����ľ����ʩչ����һ�н���ʩչ����Ľӿ��Լ�����
						������Ҫ�ض����͵ļ����Լ��жϡ�
"""
import BigWorld
from bwdebug import *
import csdefine


class SkillTargetObjImpl:
	"""
	ʵ��cell���ݵ�SkillTargetObjImpl���ݴ�������ԭ
	"""	
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if obj == None:
			return { "objType" : 0, "param" : None }
		return obj.addToPacket()
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		# ���skillIDΪ0����������Ϊ��û�и���skill�����ֱ�ӷ���None
		m_data = {
			csdefine.SKILL_TARGET_OBJECT_NONE 			: SkillTargetObjNone(),
			csdefine.SKILL_TARGET_OBJECT_ENTITY 		: SkillTargetObjEntity(),
			csdefine.SKILL_TARGET_OBJECT_ENTITYS 		: SkillTargetObjEntitys(),
			csdefine.SKILL_TARGET_OBJECT_POSITION 		: SkillTargetObjPosition(),
			csdefine.SKILL_TARGET_OBJECT_ITEM 			: SkillTargetObjItem(),
			csdefine.SKILL_TARGET_OBJECT_ENTITYPACKET	: SkillTargetObjEntityPacket(),
		}
		sk = m_data[ dict["objType"] ]
		sk.loadFromPacket( dict )
		return sk
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return (obj is None) or isinstance( obj, SkillTargetObjImpl )
#--------------------------------------------------------------------------------------------------------------------------------------
class SkillTargetObjNone( SkillTargetObjImpl ):
	"""
	���ܶ���Ŀ���λ�õ�ʩ������ķ�װ
	"""
	type = csdefine.SKILL_TARGET_OBJECT_NONE
	def __init__( self ):
		pass
	
	def init( self ):
		"""
		virtual method.
		"""
		pass
	
	def getType( self ):
		"""
		virtual method.
		"""
		return self.type
		
	def getObject( self ):
		"""
		virtual method.
		��ȡ��������װ�Ķ���
		�����װ����һ��entity ��ô����entity ����װ����position���ص��� ����(0,0,0)
		"""
		return None

	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: ���ط�������Ŀ����ӳ٣���λ����
		@rtype:  float
		"""
		return 0.0
		
	def getObjectPosition( self ):
		"""
		virtual method.
		��ȡĿ������λ�ã�����ʩ�� λ��ת��
		���ڰ�װ����һ��λ�õ� ֱ�ӷ��ذ�װ�ߣ� ���ڰ�װ����һ��entity���򷵻�entity����λ��
		�����װ������λ�����������װ ��ֱ�ӷ���(0,0,0)
		"""
		return ( 0.0, 0.0, 0.0 )
	
	def convertReference( self, caster ):
		"""
		virtual method.
		ת��һ���ο��ߣ��ṩ��AreaDefine��ΪĿ����գ� ���ڷ�װ����һ��λ�õĶ���
		����ο�����caster,�����װ����һ��entity����ο�����entity
		"""
		return caster
		
	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass
#-----------------------------------------------------------------------------------------------
class SkillTargetObjEntity( SkillTargetObjNone ):
	"""
	���ܶ�entity��������Ŀ��ķ�װ
	"""
	type = csdefine.SKILL_TARGET_OBJECT_ENTITY
	def __init__( self ):
		self._bigworldEntity = None

	def init( self, entity ):
		"""
		virtual method.
		"""
		self._bigworldEntity = entity
		
	def getObject( self ):
		"""
		virtual method.
		��ȡ��������װ�Ķ���
		�����װ����һ��entity ��ô����entity ����װ����position���ص��� ����(0,0,0)
		"""
		return self._bigworldEntity

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type
		
	def getObjectPosition( self ):
		"""
		virtual method.
		��ȡĿ������λ�ã�����ʩ�� λ��ת��
		���ڰ�װ����һ��λ�õ� ֱ�ӷ��ذ�װ�ߣ� ���ڰ�װ����һ��entity���򷵻�entity����λ��
		�����װ������λ�����������װ ��ֱ�ӷ���(0,0,0)
		"""
		if self._bigworldEntity == None:
			return ( 0.0, 0.0, 0.0 )
		return self._bigworldEntity.position

	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: ���ط�������Ŀ����ӳ٣���λ����
		@rtype:  float
		"""
		flySpeed = skill.getFlySpeed()
		if flySpeed > 1.0 and self._bigworldEntity != None:		# ����1m/s��С��1��/��������˲������
			return caster.position.flatDistTo( self._bigworldEntity.position ) / flySpeed
		return 0.0

	def convertReference( self, caster ):
		"""
		virtual method.
		ת��һ���ο��ߣ��ṩ��AreaDefine��ΪĿ����գ� ���ڷ�װ����һ��λ�õĶ���
		����ο�����caster,�����װ����һ��entity����ο�����entity
		"""
		return self._bigworldEntity
		
	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		id = None
		if self._bigworldEntity != None:
			id = self._bigworldEntity.id
		return { "objType" : self.getType(), "param" : id }
	
	def loadFromPacket( self, valDict ):
		"""
		virtual method.
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		eid = valDict[ "param" ]
		if type( eid ) == int and BigWorld.bots.values()[0].entities.has_key( eid ):
			self._bigworldEntity = BigWorld.bots.values()[0].entities[ eid ]
		else:
			self._bigworldEntity = None
		#	DEBUG_MSG( "entity object is lost!", valDict[ "param" ] )
#-----------------------------------------------------------------------------------------------
class SkillTargetObjPosition( SkillTargetObjNone ):
	"""
	���ܶ�λ�õ�������Ŀ��ķ�װ
	"""
	type = csdefine.SKILL_TARGET_OBJECT_POSITION
	def __init__( self ):
		self._entityPosition = ( 0.0,0.0,0.0 )

	def init( self, position ):
		"""
		virtual method.
		"""
		self._entityPosition = position
		
	def getObject( self ):
		"""
		virtual method.
		��ȡ��������װ�Ķ���
		�����װ����һ��entity ��ô����entity ����װ����position���ص��� ����(0,0,0)
		"""
		return self._entityPosition

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type
		
	def getObjectPosition( self ):
		"""
		virtual method.
		��ȡĿ������λ�ã�����ʩ�� λ��ת��
		���ڰ�װ����һ��λ�õ� ֱ�ӷ��ذ�װ�ߣ� ���ڰ�װ����һ��entity���򷵻�entity����λ��
		�����װ������λ�����������װ ��ֱ�ӷ���(0,0,0)
		"""
		return self._entityPosition

	def convertReference( self, caster ):
		"""
		virtual method.
		ת��һ���ο��ߣ��ṩ��AreaDefine��ΪĿ����գ� ���ڷ�װ����һ��λ�õĶ���
		����ο�����caster,�����װ����һ��entity����ο�����entity
		"""
		return caster
		
	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: ���ط�������Ŀ����ӳ٣���λ����
		@rtype:  float
		"""
		flySpeed = skill.getFlySpeed()
		if flySpeed > 1.0:		# ����1m/s��С��1��/��������˲������
			return caster.position.flatDistTo( self._entityPosition ) / flySpeed
		return 0.0
		
	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" :  self._entityPosition  }
		
	def loadFromPacket( self, valDict ):
		"""
		virtual method.
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._entityPosition = valDict[ "param" ]
#-----------------------------------------------------------------------------------------------
class SkillTargetObjItem( SkillTargetObjNone ):
	"""
	���ܶ���Ʒ��������Ŀ��ķ�װ
	"""
	type = csdefine.SKILL_TARGET_OBJECT_ITEM
	def __init__( self ):
		self._toteID = 0
		self._ownerID = 0

	def init( self, toteID, ownerID ):
		"""
		"""
		self._toteID = toteID
		self._ownerID = ownerID
		
	def getOwner( self ):
		"""
		�����Ʒ��ӵ����ʵ��
		"""
		try:
			owner = BigWorld.bots.values()[0].entities[ self._ownerID ]
		except KeyError:
			return None
		return owner
	
	def getToteID( self ):
		return self._toteID
		
	def getType( self ):
		"""
		virtual method.
		"""
		return self.type
		
	def getObject( self ):
		"""
		virtual method.
		��ȡ��������װ�Ķ���
		�����װ����һ��entity ��ô����entity ����װ����position���ص��� ����(0,0,0)
		"""
		owner = self.getOwner()
		if owner == None:
			ERROR_MSG( "can not find entity:%i" % self._ownerID )
			return None

		if not self.getOwner().isReal():
			ERROR_MSG( "use is real entity only!" )
			return
			
		try:
			entity = owner.kitbags[1].getByTote( self._toteID )
		except IndexError:
			ERROR_MSG( "Receiver %i toteID %i not exist!" % owner.id, self._toteID )
			return None
			
		return entity
		
	def getObjectPosition( self ):
		"""
		virtual method.
		��ȡĿ������λ�ã�����ʩ�� λ��ת��
		���ڰ�װ����һ��λ�õ� ֱ�ӷ��ذ�װ�ߣ� ���ڰ�װ����һ��entity���򷵻�entity����λ��
		�����װ������λ�����������װ ��ֱ�ӷ���(0,0,0)
		"""
		return self.getOwner().position

	def convertReference( self, caster ):
		"""
		virtual method.
		ת��һ���ο��ߣ��ṩ��AreaDefine��ΪĿ����գ� ���ڷ�װ����һ��λ�õĶ���
		����ο�����caster,�����װ����һ��entity����ο�����entity
		"""
		return self.getOwner()
		
	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: ���ط�������Ŀ����ӳ٣���λ����
		@rtype:  float
		"""
		return 0.0
		
	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" :  ( self._toteID, self._ownerID )  }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._toteID, self._ownerID = valDict[ "param" ]

#-----------------------------------------------------------------------------------------------
class SkillTargetObjEntityPacket( SkillTargetObjNone ):
	"""
	ӵ�ж��entity�Ķ���İ�
	"""
	type = csdefine.SKILL_TARGET_OBJECT_ENTITYPACKET
	def __init__( self ):
		self._entitys = []
		
	def init( self, entitys ):
		"""
		"""
		self._entitys = entitys

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type
	
	def entityIDToInstance( self , entityIDs ):
		"""
		"""
		self._entitys = []
		for eid in entityIDs:
			if BigWorld.bots.values()[0].entities.has_key( eid ):
				self._entitys.append( BigWorld.bots.values()[0].entities[ eid ] )

	def instanceToEntityID( self ):
		"""
		"""
		entityIDs = []
		for e in self._entitys:
			if BigWorld.bots.values()[0].entities.has_key( e.id ):
				entityIDs.append( e.id )
		return entityIDs
		
	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""

		return { "objType" : self.getType(), "param" :  self.instanceToEntityID() }
		
	def getObject( self ):
		"""
		"""
		return self._entitys
		
	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self.entityIDToInstance( valDict[ "param" ] )

#-----------------------------------------------------------------------------------------------
class SkillTargetObjEntitys( SkillTargetObjEntity ):
	"""
	���ܶԶ�ʩչ����ķ�װ
	"""
	type = csdefine.SKILL_TARGET_OBJECT_ENTITYS
	def __init__( self ):
		SkillTargetObjEntity.__init__( self )

	def init( self, entity ):
		"""
		virtual method.
		"""
		SkillTargetObjEntity.init( self, entity )
		
			
#-----------------------------------------------------------------------------------------------
#��������ʩչ��װ������Ŀ��λ��
def createTargetObjNone():
	return SkillTargetObjNone()

#��������ʩչ��װ���󣬵�entity
def createTargetObjEntity( entity ):
	if entity == None:return None
	inst = SkillTargetObjEntity()
	inst.init( entity )
	return inst

#��������ʩչ��װ���󣬶�ʩչ����
#�÷�װ����������Ͳ�ͬ�����͵�entity��һ���ģ���Ϊ�ͻ����޷�ȷ�����ʩչ�������ǰ��
#�ͻ��˴�������Ҫô��һ��λ��Ҫô��һ��entityȻ���ɷ������ҵ��ܱ�ʩչ�Ķ������ͨ��
#createTargetObjEntityPacket����������ͻ��ˣ��ͻ��˶����Ƕ���ʾʩչ��Ч
def createTargetObjEntitys( entity ):
	if entity == None:return None
	inst = SkillTargetObjEntitys()
	inst.init( entity )
	return inst

#��������ʩչ��װ����λ��
def createTargetObjPosition( position ):
	if position == None:return None
	inst = SkillTargetObjPosition()
	inst.init( position )
	return inst

#��������ʩչ��װ������Ʒ
def createTargetObjItem( toteID, ownerID ):
	if ownerID == 0:return None
	inst = SkillTargetObjItem()
	inst.init( toteID, ownerID )
	return inst
	
#����entity������һ�����ڶ�ʩչ���� ���ظ��ͻ��˲��Ź�Ч
def createTargetObjEntityPacket( entitys ):
	if entitys == 0:return None
	inst = SkillTargetObjEntityPacket()
	inst.init( entitys )
	return inst
	
	
# �Զ�������ʵ��ʵ��
instance = SkillTargetObjImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/01/03 06:25:12  kebiao
# ����һ��������
#
# Revision 1.6  2007/11/30 07:16:32  kebiao
# �޸�һ�������ӿ�
#
# Revision 1.5  2007/08/21 06:35:17  kebiao
# ����entity��ʩ�ż��ܺ��Ϊghost��ʱ�򣬼��ܴ���������飬ʱ�Ҳ���
# entityID��һ��BUG
#
# Revision 1.4  2007/08/16 06:54:28  kebiao
# add method:convertReference
# ת��һ���ο��ߣ��ṩ��AreaDefine��ΪĿ����գ� ���ڷ�װ����һ��λ�õĶ���
# ����ο�����caster,�����װ����һ��entity����ο�����entity
#
# Revision 1.3  2007/08/15 03:17:42  kebiao
# ��Ϊս��ϵͳ�ͼ���ϵͳ�ĸı���޸��˴�ģ������漰�Ķ���
#
# Revision 1.2  2007/08/03 07:37:13  kebiao
# ����һ��entityIDΪNone ���ж�
#
# Revision 1.1  2007/07/20 02:41:10  kebiao
# ����ʩչ����ķ�װ
#
# 
# 