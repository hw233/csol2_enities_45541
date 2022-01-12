# -*- coding: gb18030 -*-

# 10 级剧情副本 
# alienbrain://PROJECTSERVER/创世Online/绿色版本/09_游戏世界/05_副本设计/04_剧情副本/10级剧情副本.docx
# programmed by mushuang 

from SpaceCopy import SpaceCopy
import BigWorld
import csdefine

SPACE_SKILL_BUFF_ID = 22019
# 限制的行为
STATE = csdefine.ACTION_FORBID_CHANGE_MODEL | csdefine.ACTION_FORBID_VEHICLE

class SpaceCopyBeforeNirvana( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spaceSkills = { csdefine.CLASS_FIGHTER:[], \
							csdefine.CLASS_SWORDMAN:[], \
							csdefine.CLASS_ARCHER:[], \
							csdefine.CLASS_MAGE:[], \
							}
		
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 获取进入副本要展开的画卷ID
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerClass" ] = entity.getClass()
		scrollID = entity.popTemp( "ScrollIDOnEnter" )
		if scrollID is not None:
			packDict["ScrollIDOnEnter"] = scrollID
		return packDict
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		self.spaceSkills[csdefine.CLASS_FIGHTER] = [ int( skillID ) for skillID in section.readString( "fighterSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_SWORDMAN] = [ int( skillID ) for skillID in section.readString( "swordmanSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_ARCHER] = [ int( skillID ) for skillID in section.readString( "archerSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_MAGE] = [ int( skillID ) for skillID in section.readString( "mageSkills" ).split( ";" ) ]
		
	def canUseSkill( self, playerEntity, skillID ):
		"""
		判断是否允许玩家使用场景特定技能
		"""
		return skillID in self.spaceSkills[playerEntity.getClass()]
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		baseMailbox.cell.actCounterInc( STATE )
		baseMailbox.client.initSpaceSkills( self.spaceSkills[params["playerClass"]], csdefine.SPACE_TYPE_BEFORE_NIRVANA )
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		baseMailbox.cell.actCounterDec( STATE )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def requestInitSpaceSkill( self, playerEntity ):
		# 初始化副本技能
		playerEntity.client.initSpaceSkills( self.spaceSkills[ playerEntity.getClass() ], csdefine.SPACE_TYPE_BEFORE_NIRVANA )

