# -*- coding: gb18030 -*-
#
# $Id: FloatName.py,v 1.28 2008-08-16 03:30:41 phw Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import csdefine
import Const
import WordsProfanity
import event.EventCenter as ECenter
from ChatFacade import chatFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from EntityAttachment import EntityAttachment
from BubbleTip import BubbleTip
from DoubleName import DoubleName, RoleDoubleName
from LabelGather import labelGather
from guis.otheruis.FlyText import *
from cscollections import Queue
from Function import Functor
import ResMgr

class FloadNameMgr :
	
	def __init__( self ) :
		self.__pyFNames = {}
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_NEAR, self.__onNearSpeak )
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_TEAM, self.__onTeammateSpeak )
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.__onNPCSpeak ) # NPC说话泡泡

		self.__triggers = {}
		self.__triggers["EVT_ON_ENTITY_HP_CHANGED"] = self.__onEntityHPChanged
		self.__triggers["EVT_ON_ENTITY_HP_MAX_CHANGED"] = self.__onEntityHPChanged
		for key in self.__triggers :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onNearSpeak( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		附近 entity 发言
		"""
		pyFName = self.__pyFNames.get( spkID, None )
		if pyFName :
			pyFName.showMsg_( msg )

	def __onTeammateSpeak( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		队友发言
		"""
		pyFName = self.__pyFNames.get( spkID, None )
		if not pyFName : return
		if BigWorld.player().isTeamMember( spkID ) :
			pyFName.showMsg_( msg )

	def __onNPCSpeak( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		附近 NPC 发言
		"""
		pyFName = self.__pyFNames.get( spkID, None )
		speaker = BigWorld.entities.get( spkID, None )
		if pyFName :
			pyFName.showMsg_( msg, opGBLink = True )

	# -------------------------------------------------
	def __onEntityHPChanged( self, entity, hp, hpMax, oldValue ) :
		"""
		entity 的血量改变时被触发
		"""
		pyFName = self.__pyFNames.get( entity.id, None )
		if not pyFName : return
		pyFName.onHPChanged_( hp, hpMax )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def onAddFlatName( self, entID, pyFName ) :
		"""
		增加一个 floatName
		"""
		self.__pyFNames[entID] = pyFName

	def onFloatNameDisposed( self, entID, pyFName ) :
		"""
		删除一个 floatname
		"""
		if entID in self.__pyFNames :
			self.__pyFNames.pop( entID )

_fnameMgr = FloadNameMgr()

# --------------------------------------------------------------------
# implement float name base class
# --------------------------------------------------------------------
class FloatName( EntityAttachment, PyGUI ) :
	
	__cc_max_lines = 20
	
	def __init__( self, wnd ) :
		EntityAttachment.__init__( self )
		PyGUI.__init__( self, wnd )
		self.entity_ = None
		self.title_ = ""
		self.viewInfoKey_ = None			# 该键是在配置：config/client/viewinfosetting.xml 中的主键，标记是否要显示相关头顶标签
		self.attachNode = None				# 子类要设置为自己相应的头顶设置标签(不需要的可以不设置)
		self.__initialize( wnd )
		self.pyElements_ = []				# 保存所有头顶内容（必须是 python UI）
											# 注意：这个顺序必须是 从下到上
		self.__msgFadeCallback = 0
		self.triggers_ = {}
		self.registerTriggers_()

		self.__visibleSkillIDs = set()									# 用一个哈希表保存有对应图片的技能ID
		self.__loadSkillIDs()											# 导入技能ID
		self.__dmgCount = 0												# 伤害信息计数
		self.__clearDmgListCBID = 0

	def dispose( self ) :
		self.entity_ = None
		self.pyLbName_.leftDispose()
		self.pyLbName_.rightDispose()
		self.__deregisterTriggers()
		PyGUI.dispose( self )

	def __del__( self ) :
		EntityAttachment.__del__( self )
		PyGUI.__del__( self )
		if Debug.output_del_FloatName :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		uiFixer.attach( self )						# 添加到 ui 元素修正器（当屏幕分辨率改变时，重排子 UI 的位置，以致不会错位
		self.pyLbName_ = None		# 角色相关名字

	def __addBBAttachment( self ) :
		if self.entity_ is None : return
		model = self.entity_.getModel()
		height = self.entity_.getOriginalModelSize().y
		guiAttachment = GUI.BillboardAttachment()
		guiAttachment.component = self.getGui()
		guiAttachment.excursion = 0.0
		guiAttachment.position = Math.Vector3( 0, 0, 0 )
		attachNode = None
		if isinstance( model, BigWorld.PyModelObstacle ): # 静态模型
			if len( self.entity_.models ) > 0:
				model = self.entity_.models[0]
		if model is not None:
			try:
				attachNode = model.node("HP_title")
			except ValueError:
				pass
			if attachNode is None:
				try:
					attachNode = model.node("HP_body")
					guiAttachment.position = Math.Vector3( 0, height/2.0  , 0 )
				except ValueError:
					pass
			if attachNode is None and hasattr( model, "root" ):
				attachNode = model.root
				if self.entity_.getEntityType() == csdefine.ENTITY_TYPE_DROPPED_ITEM:
					guiAttachment.position = Math.Vector3( 0, height + 0.1, 0 )
				else:
					guiAttachment.position = Math.Vector3( 0, height + 1.0, 0 )
			if attachNode is None: return
			attachNode.attach( guiAttachment )
			self.attachNode = attachNode
			self.guiAttachment = guiAttachment

	# -------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.triggers_["EVT_ON_ENTITY_NAME_CHANGED"] = self.__onNameChanged
		self.triggers_["EVT_ON_ENTITY_TITLE_CHANGED"] = self.__onTitleChanged
		self.triggers_["EVT_ON_VIEWINFO_CHANGED"] = self.onViewInfoChanged_
		self.triggers_["EVT_ON_SHOW_DAMAGE_VALUE"] = self.showDamageValue_   # 普通伤害信息
		self.triggers_["EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE"] = self.showDoubleDamageValue_	# 致命伤害信息
		self.triggers_["EVT_ON_SHOW_HEALTH_VALUE"] = self.showHealthValue_   # 回血信息
		self.triggers_["EVT_ON_SHOW_MP_VALUE"] = self.showMPValue_			# 魔法信息
		self.triggers_["EVT_ON_SHOW_SKILL_NAME"] = self.showSkillName_       # 技能名称
		self.triggers_["EVT_ON_SHOW_REST_STATUS"] = self.showRestStatus_       # 抵抗状态
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.triggers_ :
			ECenter.unregisterEvent( key, self )
		self.triggers_ = {}

	# -------------------------------------------------
	def __onResolutionChanged( self, preReso ) :
		"""
		当屏幕分辨率改变时被调用，preReso 为改变前的屏幕分辨率
		"""
		self.layout_()

	def __onNameChanged( self, id, name ) :
		if self.entity_ == None:return
		if id == self.entity_.id:
			self.fName = name

	def __onTitleChanged( self, entity, oldTitle, newTitle, titleColor = None ) :
		if self.entity_ != entity : return
		if self.entity_.getEntityType() == csdefine.ENTITY_TYPE_CITY_MASTER:	#城主npc单独显示为占领帮会名称
			return
		self.title = newTitle
		if titleColor :
			self.pyLbName_.rightColor = titleColor
		else :
			self.pyLbName_.rightColor = 0, 255, 255, 255


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def layout_( self ) :
		preTop = 0
		for pyElem in self.pyElements_ :
			if not pyElem.visible : continue
			pyElem.center = 0.0
			pyElem.bottom = preTop
			preTop = pyElem.top - 4.0
		self.height = -preTop

	# -------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		"""
		显示信息改变时被触发
		注：重写该方法后，一定要回调，并且放到最后回调
		"""
		if self.viewInfoKey_ != infoKey : return
		if infoKey != "monster":
			if itemKey == "name" :
				self.pyLbName_.toggleLeftName( value )
			elif itemKey == "title" :
				if self.entity_.getTitle() != "" :
					self.pyLbName_.toggleRightName( value )
		self.layout_()

	# -------------------------------------------------------------------------
	def showDamageValue_( self, entityID, value ):
		"""
		普通伤害信息
		"""
		if self.entity_ == None:return
		if self.__dmgCount > self.__cc_max_lines:return
		if self.entity_.id == entityID:
			visible = self.getTextVisible( entityID, "hitDamage" )
			if not visible: return
			player = BigWorld.player()
			petID = -1
			pet = player.pcg_getActPet()
			if pet:
				petID = pet.id
			if self.entity_.id == player.id or self.entity_.id == petID:
				# 自身伤害
				font = "dmgtext.font"
				pyFlyText = getInst( DmgText )
				pyFlyText.init( str( value ), font )
				self.__dmgCount += 1
				self.__flyDmgText( pyFlyText, entityID, 0.8, 1.0 )
				BigWorld.callback( 1.0, self.__delayFly )
			else:
				# 目标伤害
				font = "targetdmg.font"
				pyFlyText = getInst( TargetDmgText )
				pyFlyText.init( str( value ), font )
				self.__dmgCount += 1
				self.__flyDmgText( pyFlyText, entityID, 0.5, 0.1 )
				BigWorld.callback( 1.0, self.__delayFly )

	def showDoubleDamageValue_( self, entityID, value ):
		"""
		致命伤害信息
		"""
		if self.entity_ == None:return
		if self.__dmgCount > self.__cc_max_lines: return
		if self.entity_.id == entityID:
			visible = self.getTextVisible( entityID, "hitDamage" )
			if not visible: return
			player = BigWorld.player()
			petID = -1
			pet = player.pcg_getActPet()
			if pet:
				petID = pet.id
			if self.entity_.id == player.id or self.entity_.id == petID:
				# 自身伤害
				font = "dmgtext.font"
				pyFlyText = getInst( DmgText )
				pyFlyText.init( str( value ), font )
				self.__dmgCount += 1
				self.__flyDmgText( pyFlyText, entityID, 0.8, 1.0 )
				BigWorld.callback( 1.0, self.__delayFly )
			else:
				# 目标伤害
				font = "targetdmg_bg.font"
				pyFlyText = getInst( TargetDmgText )
				pyFlyText.init( str( value ), font )
				self.__dmgCount += 1
				self.__flyDmgText( pyFlyText, entityID, 0.5, 0.1 )
				BigWorld.callback( 1.0, self.__delayFly )

	def __delayFly( self ):
		if self.__dmgCount:
			self.__dmgCount -= 1

	def __flyDmgText( self, pyFlyText, entityID, lastTime, sizeScale ):
			self.addPyChild( pyFlyText )
			pyFlyText.bottom = 16
			pyFlyText.startFly( entityID, lastTime, sizeScale )

	def showHealthValue_( self, entityID, value, lastTime = 0.8 ) :
		"""
		回血信息
		"""
		if self.entity_ == None:return
		if self.entity_.id == entityID:
			visible = self.getTextVisible( entityID, "revertUpLmt" )
			if not visible: return
			pyFlyText = getInst( HealthText )							# 生命恢复
			pyFlyText.init( ( str( value ) ) )
			self.addPyChild( pyFlyText )
			pyFlyText.bottom = 16
			pyFlyText.center = self.pyLbName_.center
			pyFlyText.startFly( entityID, lastTime )

	def showMPValue_( self, entityID, value, lastTime = 0.8 ):
		"""
		魔法信息
		"""
		if self.entity_ == None:return
		if self.entity_.id == entityID:
			visible = self.getTextVisible( entityID, "revertUpLmt" )
			if not visible: return
			pyFlyText = getInst( MagicText )
			pyFlyText.init( ( str( value ) ) )
			self.addPyChild( pyFlyText )
			pyFlyText.bottom = 16
			pyFlyText.center = self.pyLbName_.center
			pyFlyText.startFly( entityID, lastTime )

	def showSkillName_( self, entityID, skillID ):
		"""
		技能名称
		"""
		if self.entity_ == None:return
		visible = self.getTextVisible( entityID, "skillName" )
		if not visible:return
		if self.entity_.id == entityID :
			orgSkillID = str( skillID )[:-3]
			if str( skillID ) in self.__visibleSkillIDs:   # 有可能不同等级的技能名称不同，单独出来处理
				orgSkillID = str( skillID )
			if not orgSkillID in self.__visibleSkillIDs : return 			# 过滤掉没有对应图片的技能
			flySkillName = getInst( FlySkillName )
			flySkillName.init( orgSkillID )
			self.addPyChild( flySkillName )
			flySkillName.startFly( entityID )
			flySkillName.center = 0
			flySkillName.bottom = 16

	def delFlyText( self, pyFlyText, time = 1.2 ):
		"""
		延迟delPyChild
		"""
		functor = Functor( self.delPyChild, pyFlyText )
		BigWorld.callback( time, functor )
	
	def showRestStatus_( self, entityID, lastTime = 1.2 ):
		"""
		显示抵抗状态
		"""
		
		if  self.entity_ == None or self.entity_.id != entityID:return
		pyFlyText = getInst( FlyRestText )
		pyFlyText.init()
		self.addPyChild( pyFlyText )
		pyFlyText.startFly( entityID, lastTime )
		pyFlyText.center = 0
		pyFlyText.bottom = 16

	def getTextVisible( self, entityID, itemKey ):
		player = BigWorld.player()
		playerId = player.id
		actPet = player.pcg_getActPet()
		target = player.targetEntity
		petId = 0
		targetId = 0
		visible = True
		infoKey = ""
		if actPet:
			petId = actPet.id
		if target and target.id != playerId:
			targetId = target.id
		if entityID == playerId:
			infoKey = "roleCombat"
		elif entityID == petId:
			infoKey = "petCombat"
		if not entityID in [playerId, petId]:
			infoKey = "targetCombat"
		if infoKey == "":return visible
		else:
			visible = rds.viewInfoMgr.getSetting( infoKey, itemKey )
		return visible

	def __loadSkillIDs( self ) :
		"""
		初始化时导入存在对应图片的技能ID
		"""
		section = ResMgr.openSection( "maps/skillnames" )
		for name in section.keys() :
			sName = name.split( "." )[0]
			if sName == "" : continue
			self.__visibleSkillIDs.add( sName )

	# ----------------------------------------------------------------------------------------

	def showMsg_( self, msg, opGBLink = False ): #动态显示聊天泡泡，只有说话时才显示
		if self.entity_ == None:return
		msg_temp = msg.split("/ltime")
		if len( msg_temp ) > 1 :
			msg = msg_temp[0]
			msg_lasttime = int(msg_temp[1])
		else :
			msg_lasttime = 5.0
		self.bubStyle = rds.viewInfoMgr.getSetting( "bubble", "style" ) #泡泡风格
		self.pyBubTip_ = getattr( self, "pyBubTip_", None )
		if self.pyBubTip_: #保证一次只有一个泡泡
			if self.pyBubTip_ in self.pyElements_:
				self.pyElements_.remove( self.pyBubTip_ )
				self.delPyChild( self.pyBubTip_ )
				self.pyBubTip_.dispose()
		if rds.viewInfoMgr.getSetting( "bubble", "visible" ) :			# 聊天泡泡不再区分自身，他人，怪物，NPC
			self.pyBubTip_ = BubbleTip()
			self.addPyChild( self.pyBubTip_ )
			self.pyElements_.append( self.pyBubTip_ )
			self.pyBubTip_.show( msg, self.bubStyle, opGBLink )
			def fade() :
				self.pyBubTip_.hide()
				if self.pyBubTip_ in self.pyElements_:
					self.pyElements_.remove( self.pyBubTip_ )
				self.delPyChild( self.pyBubTip_ )
				self.pyBubTip_.dispose()
				self.__msgFadeCallback = 0
			self.__msgFadeCallback = BigWorld.callback( msg_lasttime, fade )
		self.layout_()

	# -------------------------------------------------
	def onHPChanged_( self, hp, hpMax ) :
		pass
		
	def onAttachEntity_( self ):
		"""
		初始化entity数据
		"""
		pass
		
	def onDetachEntity_( self ):
		"""
		在这里做这种清理工作，恢复gui
		"""
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		if self.entity_ is None:return
		self.fName = self.entity_.getName()
		self.title = self.entity_.getTitle()
		if self.entity_.getEntityType() == csdefine.ENTITY_TYPE_CITY_MASTER:
			self.title = self.entity_.tongName
		self.layout_()

	def onLeaveWorld( self ) :
		pass

	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )

	def isMonsterName( self ):
		return False
		
	def attachEntity( self, entity ):
		"""
		绑定entity
		"""
		_fnameMgr.onAddFlatName( entity.id, self )
		self.entity_ = entity
		self.onAttachEntity_()
		self.visible = True
		self.__addBBAttachment()
		self.layout_()
		
	def detachEntity( self ):
		"""
		与entity解除绑定
		"""
		if self.entity_:
			_fnameMgr.onFloatNameDisposed( self.entity_.id, self )
		self.visible = False
		self.entity_ = None
		self.title_ = ""
		if self.attachNode:   # 清除node上面旧的附加UI
			self.attachNode.detach( self.guiAttachment )
		self.attachNode = None				# 子类要设置为自己相应的头顶设置标签(不需要的可以不设置)
		self.pyLbName_.toggleDoubleName( False )
		self.__msgFadeCallback = 0
		self.onDetachEntity_()
		
	def bindWithEntity( self ):
		"""
		判断是否已经和entity绑定
		"""
		return  self.entity_ != None

	# -------------------------------------------------
	def flush( self ) :
		"""
		刷新模型（更改模型后，将原模型的头顶信息迁移过去）
		"""
		if self.entity_ is None:return
		self.__addBBAttachment()
		self.fName = self.entity_.getName()
		self.title = self.entity_.getTitle()
		if self.entity_.getEntityType() == csdefine.ENTITY_TYPE_CITY_MASTER:
			self.title = self.entity_.tongName
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getFName( self ) :
		return self.pyLbName_.leftName

	def _setFName( self, name ) :
		self.pyLbName_.leftName = name
		self.pyLbName_.toggleLeftName( False )
		if self.entity_ is None or not self.entity_.inWorld:return
		if self.isMonsterName() and self.entity_.hasFlag( csdefine.ENTITY_FLAG_ALAWAY_HIDE_NAME ): return
		if self.viewInfoKey_ :
			self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ))
		else :
			self.pyLbName_.toggleLeftName( name != "" )
		self.layout_()

	# ---------------------------------------
	def _getTitle( self ) :
		return self.title_

	def _setTitle( self, title ) :
		self.title_ = title
		if title == "" :
			self.pyLbName_.toggleRightName( False )
		else :
			entityType = self.entity_.getEntityType()
			if not entityType in  [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_DANCE_KING]:
				title = labelGather.getText( "FloatName:floatName", "title" )%title
			self.pyLbName_.rightName = title
			if self.viewInfoKey_ :
				self.pyLbName_.toggleRightName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "title" ))
			else :
				self.pyLbName_.toggleRightName( title != "" )
		self.layout_()

	def _setColor( self, titleColor ):
		if titleColor is not None:
			self.pyLbName_.rightColor = titleColor

	def _getColor( self ):
		return self.pyLbName_.rightColor
		
	def _getLeftColor( self ) :
		return self.pyLbName_.leftColor

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	fName = property( _getFName, _setFName )
	title = property( _getTitle, _setTitle )
	color = property( _getColor, _setColor )
	leftColor = property( _getLeftColor )
