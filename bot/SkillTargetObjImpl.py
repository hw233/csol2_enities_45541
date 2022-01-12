# -*- coding: utf-8 -*-
#
# $Id: SkillTargetObjImpl.py 690 2009-06-11 02:58:18Z qilan $

"""
接收者，如果用C++角度来看，则我们可以视这个参数为一个抽象对象CReceiver，
						该对象的作用就是抽象对于施法来说所需要的一些接口，然后让一切可能的接收者都
						继承于它，如位置（CReceiverPosition）、entity（CReceiverEntity）、
						玩家身上物品（CReceiverItem）等，可以根据抽象的接口实现自己的实现，
						这样技能在施展时就能统一接口，且不关心具体的施展对象，一切皆由施展对象的接口自己处理，
						或由需要特定类型的技能自己判断。
"""
import BigWorld
from bwdebug import *
import csdefine


class SkillTargetObjImpl:
	"""
	实现cell部份的SkillTargetObjImpl数据创建、还原
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
		# 如果skillID为0，则我们认为其没有附上skill，因此直接返回None
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
	技能对无目标和位置的施法对象的封装
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
		获取真正被封装的对象
		如果封装的是一个entity 那么返回entity ，封装的是position返回的是 类似(0,0,0)
		"""
		return None

	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: 返回法术击中目标的延迟，单位：秒
		@rtype:  float
		"""
		return 0.0
		
	def getObjectPosition( self ):
		"""
		virtual method.
		获取目标所在位置（用于施法 位置转向）
		对于包装者是一个位置的 直接返回包装者， 对于包装者是一个entity的则返回entity所在位置
		对与包装者是无位置属性特殊包装 则直接返回(0,0,0)
		"""
		return ( 0.0, 0.0, 0.0 )
	
	def convertReference( self, caster ):
		"""
		virtual method.
		转换一个参考者，提供给AreaDefine作为目标参照， 对于封装者是一个位置的对象
		这个参考者是caster,对与封装的是一个entity这个参考者是entity
		"""
		return caster
		
	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTargetObjImpl；
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
	技能对entity的受术或目标的封装
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
		获取真正被封装的对象
		如果封装的是一个entity 那么返回entity ，封装的是position返回的是 类似(0,0,0)
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
		获取目标所在位置（用于施法 位置转向）
		对于包装者是一个位置的 直接返回包装者， 对于包装者是一个entity的则返回entity所在位置
		对与包装者是无位置属性特殊包装 则直接返回(0,0,0)
		"""
		if self._bigworldEntity == None:
			return ( 0.0, 0.0, 0.0 )
		return self._bigworldEntity.position

	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: 返回法术击中目标的延迟，单位：秒
		@rtype:  float
		"""
		flySpeed = skill.getFlySpeed()
		if flySpeed > 1.0 and self._bigworldEntity != None:		# 至少1m/s，小于1米/秒则当作是瞬发处理
			return caster.position.flatDistTo( self._bigworldEntity.position ) / flySpeed
		return 0.0

	def convertReference( self, caster ):
		"""
		virtual method.
		转换一个参考者，提供给AreaDefine作为目标参照， 对于封装者是一个位置的对象
		这个参考者是caster,对与封装的是一个entity这个参考者是entity
		"""
		return self._bigworldEntity
		
	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTargetObjImpl；
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
	技能对位置的受术或目标的封装
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
		获取真正被封装的对象
		如果封装的是一个entity 那么返回entity ，封装的是position返回的是 类似(0,0,0)
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
		获取目标所在位置（用于施法 位置转向）
		对于包装者是一个位置的 直接返回包装者， 对于包装者是一个entity的则返回entity所在位置
		对与包装者是无位置属性特殊包装 则直接返回(0,0,0)
		"""
		return self._entityPosition

	def convertReference( self, caster ):
		"""
		virtual method.
		转换一个参考者，提供给AreaDefine作为目标参照， 对于封装者是一个位置的对象
		这个参考者是caster,对与封装的是一个entity这个参考者是entity
		"""
		return caster
		
	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: 返回法术击中目标的延迟，单位：秒
		@rtype:  float
		"""
		flySpeed = skill.getFlySpeed()
		if flySpeed > 1.0:		# 至少1m/s，小于1米/秒则当作是瞬发处理
			return caster.position.flatDistTo( self._entityPosition ) / flySpeed
		return 0.0
		
	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTargetObjImpl；
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
	技能对物品的受术或目标的封装
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
		获得物品的拥有者实例
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
		获取真正被封装的对象
		如果封装的是一个entity 那么返回entity ，封装的是position返回的是 类似(0,0,0)
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
		获取目标所在位置（用于施法 位置转向）
		对于包装者是一个位置的 直接返回包装者， 对于包装者是一个entity的则返回entity所在位置
		对与包装者是无位置属性特殊包装 则直接返回(0,0,0)
		"""
		return self.getOwner().position

	def convertReference( self, caster ):
		"""
		virtual method.
		转换一个参考者，提供给AreaDefine作为目标参照， 对于封装者是一个位置的对象
		这个参考者是caster,对与封装的是一个entity这个参考者是entity
		"""
		return self.getOwner()
		
	def calcDelay( self, skill, caster ):
		"""
		virtual method.
		@return: 返回法术击中目标的延迟，单位：秒
		@rtype:  float
		"""
		return 0.0
		
	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTargetObjImpl；
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
	拥有多个entity的对象的包
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
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTargetObjImpl；
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
	技能对多施展对象的封装
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
#创建技能施展封装对象，无目标位置
def createTargetObjNone():
	return SkillTargetObjNone()

#创建技能施展封装对象，单entity
def createTargetObjEntity( entity ):
	if entity == None:return None
	inst = SkillTargetObjEntity()
	inst.init( entity )
	return inst

#创建技能施展封装对象，多施展对象
#该封装对象除了类型不同其他和单entity是一样的，因为客户端无法确定多个施展对象因此前期
#客户端传过来的要么是一个位置要么是一个entity然后由服务器找到能被施展的对象后再通过
#createTargetObjEntityPacket来打包传给客户端，客户端对他们都显示施展光效
def createTargetObjEntitys( entity ):
	if entity == None:return None
	inst = SkillTargetObjEntitys()
	inst.init( entity )
	return inst

#创建技能施展封装对象，位置
def createTargetObjPosition( position ):
	if position == None:return None
	inst = SkillTargetObjPosition()
	inst.init( position )
	return inst

#创建技能施展封装对象，物品
def createTargetObjItem( toteID, ownerID ):
	if ownerID == 0:return None
	inst = SkillTargetObjItem()
	inst.init( toteID, ownerID )
	return inst
	
#创建entity包对象，一般用于多施展对象 返回给客户端播放光效
def createTargetObjEntityPacket( entitys ):
	if entitys == 0:return None
	inst = SkillTargetObjEntityPacket()
	inst.init( entitys )
	return inst
	
	
# 自定义类型实现实例
instance = SkillTargetObjImpl()

#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/01/03 06:25:12  kebiao
# 加入一个错误处理
#
# Revision 1.6  2007/11/30 07:16:32  kebiao
# 修改一处废弃接口
#
# Revision 1.5  2007/08/21 06:35:17  kebiao
# 修正entity在施放技能后变为ghost的时候，技能打包数据重组，时找不到
# entityID的一个BUG
#
# Revision 1.4  2007/08/16 06:54:28  kebiao
# add method:convertReference
# 转换一个参考者，提供给AreaDefine作为目标参照， 对于封装者是一个位置的对象
# 这个参考者是caster,对与封装的是一个entity这个参考者是entity
#
# Revision 1.3  2007/08/15 03:17:42  kebiao
# 因为战斗系统和技能系统的改变而修改了此模块相关涉及的东西
#
# Revision 1.2  2007/08/03 07:37:13  kebiao
# 加入一个entityID为None 的判断
#
# Revision 1.1  2007/07/20 02:41:10  kebiao
# 技能施展对象的封装
#
# 
# 