# -*- coding: gb18030 -*-
#
# $Id: PBItem.py,v 1.7 2008-07-21 02:57:41 huangyongwei Exp $

"""
implement quick item class
2006/07/15: writen by huangyongwei
"""

import csdefine
from guis import *
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
from Helper import courseHelper
from LabelGather import labelGather
from SKItemDetector import SKIDetector
import csconst
import csstatus

class PBItem( Item ):
	__cc_colors = {}
	__cc_colors[ "default" ] = ( 255, 255, 255, 255 )
	__cc_colors[ "unableUse" ] = ( 150, 70, 70, 255 )

	def __init__( self, item, index ):
		Item.__init__( self, item )
		self.dragMark = DragMark.PET_QUICK_BAR
		self.__initialize( item )
		self.__index = index

		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "PET_QB_GRID_%i" % ( index + 1 ), self.spellItem )

	def __initialize( self, item ) :
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True

		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.font = "system_small.font"
		self.__pyLbAmount.color = 255, 228, 193, 255
		self.__pyLbAmount.text = ""
		self.autoUseSign = False

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# ��������һ�Σ���8֡
		self.__pyOverCover.cycle = 0.4										# ѭ������һ�εĳ���ʱ�䣬��λ����
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.clear()

	def dispose( self ) :
		Item.dispose( self )
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PET_BEGIN_COOLDOWN"] = self.__beginCooldown
		self.__triggers["EVT_ON_PET_MP_CHANGE"]  	 = self.__onMPChanded
		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( self, trigger )
		self.__triggers = {}

	# -------------------------------------------------
	def __cancelCooldown( self ) :
		if self.itemInfo is not None :
			self.itemInfo.unlock()
		self.__pyCDCover.reset( 0 )

	def __beginCooldown( self, cooldownType, lastTime ) :
		if self.itemInfo is None : return
		if self.itemInfo.isCooldownType( cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def __onMPChanded( self, mp, mpMax ) :
		"""
		����MP �ı��֪ͨ�˴�
		"""
		self.updateIconState()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def checkForDetection_( self, newItemInfo ) :
		"""
		����Ƿ���Ҫ��̽�����и���
		"""
		SKIDetector.unbindPyItem( self )						# ����������̽���������

		if newItemInfo is None : return

		spell = newItemInfo.getSpell()
		if spell is None : return

		rangeMax = csconst.PET_FORCE_FOLLOW_RANGE
		SKIDetector.bindPyItem( self, ( "PET", rangeMax ) )		# ��ӵ�̽����

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if pyDragged.itemInfo is None: 
			toolbox.itemCover.normalizeItem()
			return False
		Item.onDragStart_( self, pyDragged )
		return True

	def onDrop_( self, pyTarget, pyDropped ):
		Item.onDrop_( self, pyTarget, pyDropped )
		if pyDropped.itemInfo is None : return True
		player = BigWorld.player()
		if pyDropped.dragMark == DragMark.PETSKILL_BAR: 					# �ӳ��＼�����
			player.pcg_updatePetQBItem( self.index, pyDropped.itemInfo.baseItem )
		elif pyDropped.dragMark == DragMark.PET_QUICK_BAR:					# ��������֮���Ϸ�
			player.pcg_exchangePetQBItem( pyDropped.index, self.index )
		return True

	def onDragStop_( self, pyDragged ):
		Item.onDragStop_( self, pyDragged )
		if ruisMgr.isMouseHitScreen():
			BigWorld.player().pcg_updatePetQBItem( self.index, None )

	def onLClick_( self, mods ) :
		Item.onLClick_( self, mods )
		self.spellItem()
		return

	def onRClick_( self, mods ) :
		Item.onRClick_( self, mods )
		BigWorld.player().pcg_toggleAutoUsePetQBItem( self.index )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		"""
		triggered by base
		"""
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def update( self, itemInfo ) :
		self.checkForDetection_( itemInfo )
		Item.update( self, itemInfo )
		if itemInfo is not None :
			self.__pyLbAmount.text = ""
			if itemInfo.countable and itemInfo.amount > 1 :
				self.__pyLbAmount.text = str( itemInfo.amount )
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )
			self.updateIconState()
		else :
			# ���û����Ʒ�˵�Ȼ����������ʾ
			self.__pyCDCover.reset( 0 )
			self.color = PBItem.__cc_colors[ "default" ]

	# -------------------------------------------------
	def spellItem( self ):
		if self.itemInfo is not None :
			self.itemInfo.spell()
		return True

	def clear( self ) :
		"""
		clean the item
		"""
		Item.clear( self )
		self.__pyLbAmount.text = ""
		self.__cancelCooldown()
		self.autoUseSign = False
		SKIDetector.unbindPyItem( self )						# ��̽�����Ƴ�

	def updateIconState( self ):
		"""
		���¿����ͼ���״̬  ��ɫ����ɫ
		"""
		player = BigWorld.player()
		itemInfo = self.itemInfo

		if itemInfo is not None :
			#��ʾ/ȡ���Զ��ͷŵı�־
			if itemInfo.autoUse:
				# �Զ�����״̬
				self.autoUseSign = True
			else:
				self.autoUseSign = False
			#����ͼ�����ɫ
			state = itemInfo.validTarget()
			if state in [ csstatus.SKILL_INTONATING, csstatus.SKILL_NOT_READY, csstatus.SKILL_GO_ON ]:
				self.color = PBItem.__cc_colors[ "default" ]
				return
			elif state == csstatus.SKILL_TOO_FAR :
				# ����ԶҪ���г���
				if player.pcg_getActPet() and player.position.distTo( player.pcg_getActPet().position ) > csconst.PET_FORCE_FOLLOW_RANGE:
					# ����̫Զ��ɫ
					self.color = PBItem.__cc_colors[ "unableUse" ]
					return
			else:
				# ����ʹ�ã���ʾ��ɫ
				self.color = PBItem.__cc_colors[ "unableUse" ]
				return

		# ������ʾ
		self.color = PBItem.__cc_colors[ "default" ]

	def onDetectorTrigger( self ) :
		"""Ŀ��������ص�"""
		self.updateIconState()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		if self.itemInfo is None :
			self.description = labelGather.getText( "quickbar:pbItem", "tipsSkillItem" )
		Item.onDescriptionShow_( self )

	def onDescriptionHide_( self ) :
		"""
		������뿪ʱ�����ã������������
		"""
		Item.onDescriptionHide_( self )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getIndex( self ) :
		return self.__index

	def _setAutoUseSign( self , show ):
		"""
		�����Զ��ͷŵı�־���߿������ת��������
		"""
		self.gui.y_light.visible = show

	def _getAutoUseSign( self ):
		"""
		�鿴�Ƿ���ʾ�Զ��ͷŵı�־
		"""
		return self.gui.y_light.visible

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	index = property( _getIndex )
	autoUseSign = property( _getAutoUseSign, _setAutoUseSign)			#����ȡ�������Զ�ʹ�ñ�־����ʾ