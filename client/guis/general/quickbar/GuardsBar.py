# -*- coding: gb18030 -*-
#
# $Id: AutoFightBar.py,v 1.15 2008-08-26 02:18:33 huangyongwei Exp $

import event.EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from AutoFightItem import AutoFightItem
from LabelGather import labelGather
from ItemsFactory import SkillItem
import skills as Skills
import csconst
import csdefine
import csstatus

class GuardsBar( PyGUI ):
	
	def __init__( self, qb ):
		PyGUI.__init__( self, qb )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.__spellingItems = []
		self.__invalidItems = []
		self.__cancelCoverCBID = 0
		self.__initialize( qb )

	def __initialize( self, qb ) :
		for name, item in qb.children :
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = GuardItem( item.icon, self )
			pyItem.index = index
			description = labelGather.getText( "quickbar:guardsBar", "tipsGuardItem" )
			pyItem.description = description
			pyItem.onLMouseDown.bind( self.__onBarMouseDown )
			pyItem.onMouseEnter.bind( self.__onBarMouseEnter )
			pyItem.onMouseLeave.bind( self.__onBarMouseLeave )
			self.__pyItems[index] = pyItem

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# ������ʾ����ʩ�ŵļ���
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# ���ؼ��ܵĸ�����ʾ
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# ��������ü���ʱ��ʾ��ɫ�߿�
		self.__triggers["EVT_ON_PLAYER_ADD_MAPSKILL"]	= self.__onRoleAddMapSkill			# �����ػ�����
		self.__triggers["EVT_ON_PLAYER_REMOVE_MAPSKILL"]	= self.__onRoleRemoveMapSkill	# �Ƴ��ػ�����
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onUpdateItem( self, gbIndex, itemInfo ) :
		player = BigWorld.player()
		if self.__pyItems.has_key( gbIndex ):
			pyItem = self.__pyItems[gbIndex]
			pyItem.update( itemInfo )
			pyItem.updateIconState()
			
	def __onShowSpellingCover( self, skillID ) :
		"""
		�ø���ͼ���ʶ����ʩ�ŵļ���
		@param		skillID	:	����ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__spellingItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__spellingItems.append( pyItem )
				toolbox.itemCover.showSpellingItemCover( pyItem )

	def __onHideSpellingCover( self ) :
		"""
		����ͼ��ĸ�����ʾ״̬
		"""
		for pyItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		��������ü���ʱ�ú�ɫ�߿���ʾ
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidItemCovers()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# �����1����Զ�����

	def __hideInvalidItemCovers( self ) :
		"""
		���ز����ü��ܵĺ�ɫ�߿�
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__invalidItems = []

	def __onBarMouseDown( self ) :
		"""
		������򸡶�����ʧ
		"""
		toolbox.infoTip.hide()

	def __onBarMouseEnter( self, pyItem ) :
		"""
		�������򸡶������
		"""
		toolbox.infoTip.showItemTips( self, pyItem.description )

	def __onBarMouseLeave( self ) :
		"""
		����뿪�򸡶�����ʧ
		"""
		toolbox.infoTip.hide()
	
	def __onRoleAddMapSkill( self, index, skillID ):
		"""
		�����ػ�����
		"""
		if index in self.__pyItems:
			skill = Skills.getSkill( skillID )
			skInfo = SkillItem( skill )
			pyItem = self.__pyItems[index]
			pyItem.update( skInfo )
	
	def __onRoleRemoveMapSkill( self, index ):
		"""
		�Ƴ��ػ�����
		"""
		if index in self.__pyItems:
			pyItem = self.__pyItems[index]
			pyItem.update( None )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.visible = False
		self.__onHideSpellingCover()
		for index, pyItem in self.__pyItems.iteritems() :
			pyItem.gbIndex = index
			self.__onUpdateItem( index, None )

	def onEnterWorld( self ) :
		self.__pyOpenBtn.visible = True
		self.__pyCloseBtn.visible = False
	
	def initMapSkills( self, skills ):
		for index, skillID in skills.items():
			pyItem = self.__pyItems.get( index, None )
			if pyItem is None:continue
			skill = Skills.getSkill( skillID )
			skInfo = SkillItem( skill )
			pyItem.update( skInfo )
	
	def reset( self ):
		for index, pyItem in self.__pyItems.iteritems() :
			self.__onUpdateItem( index, None )

# ----------------------------------------------------------------------
# �ػ�ͼ��
# ----------------------------------------------------------------------
from guis.controls.Item import Item as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.controls.StaticText import StaticText

class GuardItem( BOItem ):
	
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.dragMark = DragMark.GUARD_QUICK_BAR
		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.visible = False
		
		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.text = ""
		
		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.visible = False
		
		self.focus = True
		self.__itemInfo = None
		self.index = -1
		self.__triggers = {}
		self.__registerTriggers()
	
	def __clearItem( self ):
		self.update( None )

	# ----------------------------------------------------------------
	# about event
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}

	def __beginCooldown( self, cooldownType, lastTime ) :
		"""
		when cooldown triggered, it will be called
		"""
		itemInfo = self.itemInfo
		if itemInfo is None :
			return
		if itemInfo.isCooldownType( cooldownType ) :
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCover.unfreeze( *cdInfo )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo:
			self.itemInfo.spell()
		return True

	def onLClick_( self, mods ) :
		BOItem.onLClick_( self, mods )
		if self.itemInfo:
			self.itemInfo.spell()
		return True

	def onDragStop_( self, pyDrogged ) :
		BOItem.onDragStop_( self, pyDrogged )
		if ruisMgr.isMouseHitScreen():
			self.update( None )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		player = BigWorld.player()
		if pyDropped.dragMark == DragMark.GUARD_LIST_PANEL:
			itemInfo = pyDropped.itemInfo
			index = pyTarget.index
			skillID = itemInfo.id
			player.addMapSkill( index, skillID )
		elif pyDropped.dragMark == DragMark.GUARD_QUICK_BAR :
			if pyTarget.itemInfo:
				tIndex = pyTarget.index
				tSkillID = pyTarget.itemInfo.id
				dIndex = pyDropped.index
				dSkillID = pyDropped.itemInfo.id
				player.addMapSkill( tIndex, dSkillID )
				player.addMapSkill( dIndex, tSkillID )
			else:
				tIndex = pyTarget.index
				dIndex = pyDropped.index
				dSkillID = pyDropped.itemInfo.id
				player.addMapSkill( tIndex, dSkillID )
				player.removeMapSkill( dIndex )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		self.itemInfo = itemInfo

	def updateIconState( self ):
		"""
		written by kebiao
		���¿����ͼ���״̬  ��ɫ,��ɫ
		"""
		itemInfo = self.itemInfo
		if itemInfo is not None :
			# �����ͼ����ݶԸ���Ʒ���߼��ܶ�Ŀ��ʹ�õ����״̬������ɫ
			state = itemInfo.validTarget()
			if state in [ csstatus.SKILL_INTONATING, csstatus.SKILL_ITEM_INTONATING ]:
				# Ϊ�����Ч�� ���ܵײ������жϵ�����Щ����, ����������������漸����������ȫ����Ϊ���ܺϷ�
				# ������Ҫָ��ȥ��������������ܹ�����һЩ���������
				pass
			elif state in [ csstatus.SKILL_NOT_READY, csstatus.SKILL_ITEM_NOT_READY ]:
				# �������������жϵ��Ⱥ�˳���������
				# �����ܹ��������ʾ���� �����ж��Ѿ��Ϸ���
				itemInfo.activeState_ = 0
				self.color = ( 255, 255, 255, 255 )
			elif state == csstatus.SKILL_GO_ON:
				itemInfo.activeState_ = 0
				self.color = ( 255, 255, 255, 255 )
			elif state == csstatus.SKILL_OUTOF_MANA:
				# ������һ��Ϊ�������� ����ȱ������ ��ʾ��ɫ
				itemInfo.activeState_ = 1
				self.color = ( 0.0, 80.0, 255.0, 255.0 )
			elif state == csstatus.SKILL_MISSING_ITEM:
				# ������һ��Ϊ�������� ����ȱ������ ��ʾ��ɫ
				itemInfo.activeState_ = 2
				self.color = ( 0.0, 80.0, 255.0, 255.0 )
			else:
				# ������һ��Ϊ���벻�� ����ȱ������ ��ʾ��ɫ
				itemInfo.activeState_ = 3
				self.color = ( 100, 100, 100, 250 )

	def onDetectorTrigger( self ) :
		"""Ŀ��������ص�"""
		self.updateIconState()

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )