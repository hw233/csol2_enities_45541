# -*- coding: gb18030 -*-
#


"""
"""
import BigWorld
import csstatus
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine
#对应性别对应职业的斗舞副本NPC的className
classNames = {csdefine.GENDER_MALE:{csdefine.CLASS_FIGHTER:"10121772",  \
									csdefine.CLASS_SWORDMAN:"10121774", \
									csdefine.CLASS_ARCHER:"10121776",   \
									csdefine.CLASS_MAGE:"10121778"      \
				},\
			  csdefine.GENDER_FEMALE:{csdefine.CLASS_FIGHTER:"10121773", \
			  						  csdefine.CLASS_SWORDMAN:"10121775",\
			  						  csdefine.CLASS_ARCHER:"10121777",  \
			  						  csdefine.CLASS_MAGE:"10121779"     \
			  }}
class SpaceCopyDance( SpaceCopy ):
	def __init__(self):
		SpaceCopy.__init__(self)
		self.spaceSkills = []
		
		
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'dbID' : entity.databaseID ,"class":entity.getClass() ,"gender":entity.getGender(),"spaceKey":entity.databaseID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		pickDict["class"] = entity.getClass()
		pickDict["gender"] = entity.getGender()
		return pickDict		
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		# 以正常的方式进入副本
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		entity = g_objFactory.getObject( classNames[params["gender"]][params["class"]] ).createEntity( selfEntity.spaceID, (42.7,0,54.7), (0,0,0), {} )
		DEBUG_MSG("create entity DanceNPC %d"%entity.id)
		
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		self.spaceSkills = [ int( skillID ) for skillID in section.readString( "spaceSkills" ).split( ";" ) ]
		
	def canUseSkill( self, playerEntity, skillID ):
		"""
		判断是否允许玩家使用场景特定技能
		"""
		return skillID in self.spaceSkills	
	