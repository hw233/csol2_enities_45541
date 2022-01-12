# -*- coding: gb18030 -*-
#
# $Id: QBItem.py,v 1.47 2008-07-21 03:02:25 huangyongwei Exp $

"""
implement quick item class
2006/07/15: writen by huangyongwei
"""

import csdefine
import csstatus
import QBShowSpecialChange
from SKItemDetector import SKIDetector
from guis import *
from keys import *
import event.EventCenter as ECenter
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.otheruis.AnimatedGUI import AnimatedGUI
import skills as Skill
from LabelGather import labelGather
from ItemsFactory import SkillItem
from config.skill.SkillTeachData import Datas as skTeachDatas
from GUIFacade.LearnSkillFacade import LearningSkill
import config.client.labels.GUIFacade as lbDatas

class QBItem( Item ) :

	__cg_tip_detect_cbid = 0
	
	def __init__( self, item, pyBinder = None ) :
		Item.__init__( self, item, pyBinder )
		self.dragMark = DragMark.QUICK_BAR
		self.__fader = GUI.AlphaShader()
		self.__fader.value = 1.0
		self.__fader.speed = 0.4
		self.__flashcbid = 0
		item.addShader( self.__fader )

		self.__gbIndex = 0
		self.__gbCopy = False													# ͼ���ϵ�����ʱ�����ж�ʱcopy���Ǽ�����Ĭ��Ϊ���� 15:27 2008-3-20 yk
		self.__shortcut = ( 0, 0 )
		self.__flashSign = True
		self.__autoParticle = "autoParticle"
		self.__triggers = {}

		self.__registerTriggers()
		self.__initialize( item )

	def __initialize( self, item ) :
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True

		self.__pySTAmount = StaticText( item.lbAmount )
		self.__pySTAmount.font = "system_small.font"
		self.__pySTAmount.color = 255, 228, 193, 255
		self.__pySTAmount.text = ""

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# ��������һ�Σ���8֡
		self.__pyOverCover.cycle = 0.4										# ѭ������һ�εĳ���ʱ�䣬��λ����
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )
		
		self.isNotInit = True												# ��Ϊ��ɫ��ʼ����

		self.clear()

	def dispose( self ) :
		Item.dispose( self )
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		self.__triggers["EVT_ON_ROLE_MP_CHANGED"] = self.__onMPChanded
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] = self.__onKigbagChanged
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKigbagChanged
		self.__triggers["EVT_ON_EQUIPBAG_ADD_ITEM"] = self.__onKigbagChanged
		self.__triggers["EVT_ON_EQUIPBAG_REMOVE_ITEM"] = self.__onKigbagChanged
		self.__triggers["EVT_ON_ACTWORD_CHANGED"] = self.__onActWordChanged
		self.__triggers["EVT_ON_REFRESH_QBITEM"] = self.__refreshQBItem
		self.__triggers["EVT_ON_COMBATCOUNT_CHANGED"] = self.__combatCountChanged		#�񶷵�ı�
		self.__triggers["EVT_ON_ROLE_EN_CHANGED"] = self.__onENChanged					#��Ծֵ�ı�
		self.__triggers["EVT_ON_PLAYER_POSTURE_CHANGED"]	= self.__onPostureChange	# ��̬�ı�

		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( self, trigger )

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
			if self.isMouseHit():
				self.onDescriptionShow_()
	# -------------------------------------------------
	def __handleShortcut( self ) :
		if self.visible :
			self.spellItem()
			return True
		return False

	def __handleSelfShortcut( self ):
		if self.visible :
			self.spellItemToSelf()
			return True
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		if self.itemInfo is None : return None
		description = QBShowSpecialChange.descriptionChange( self )  		# ���description��Ϣ����������
		self.description = description
		Item.onDescriptionShow_( self )
		leaveTime = self.itemInfo.getCooldownInfo()[0]									#��ȴʣ��ʱ��
		if leaveTime > 0 and self.isMouseHit():
			QBItem.__cg_tip_detect_cbid = BigWorld.callback( 1.0, self.onDescriptionShow_ )	# 1����������
		else:
			BigWorld.cancelCallback( QBItem.__cg_tip_detect_cbid ) 	#ȡ��ˢ��������Ϣ
			QBItem.__cg_tip_detect_cbid = 0

	def onDescriptionHide_( self ) :
		"""
		������뿪ʱ�����ã������������
		"""
		Item.onDescriptionHide_( self )
		BigWorld.cancelCallback( QBItem.__cg_tip_detect_cbid ) 	#ȡ��ˢ��������Ϣ
		QBItem.__cg_tip_detect_cbid = 0

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		pyTopParent = self.pyTopParent
		if  self.itemInfo is not None and hasattr(pyTopParent, "isLocked" ) and pyTopParent.isLocked():
			BigWorld.player().statusMessage( csstatus.QB_HAS_LOCKED )
			return False
		if pyDragged.itemInfo is None: 
			toolbox.itemCover.normalizeItem()
			return False
		Item.onDragStart_( self, pyDragged )
		if self.dragMark == DragMark.QUICK_BAR and \
		not ( self.gbIndex >= 30 and self.gbIndex <= 35 ) \
		and ( pyDragged.itemInfo  is not None ):
			rds.ruisMgr.hideBar.enterShow()
			rds.ruisMgr.hideBar.hightlightLack()
			self.pyTopParent.hightlightLack()
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		pyTopParent = self.pyTopParent
		if hasattr( pyTopParent, "isLocked" ) and pyTopParent.isLocked():
			BigWorld.player().statusMessage( csstatus.QB_HAS_LOCKED )
			return False
		if pyDropped.itemInfo is None : return True
		Item.onDrop_( self, pyTarget, pyDropped )
		player = BigWorld.player()
		baseItem = pyDropped.itemInfo.baseItem
		if pyDropped.dragMark == DragMark.KITBAG_WND and not baseItem.isEquip() and baseItem.query( "spell", 0 ) :
			player.qb_updateItem( self.gbIndex, csdefine.QB_ITEM_KITBAG, baseItem )
			return True
		elif pyDropped.dragMark == DragMark.SKILL_WND :
			if self.itemInfo and not self.isNotInit:
				ECenter.fireEvent( "EVT_ON_QB_REMOVE_INITE_SKILL", self.itemInfo.id, self.gbIndex )
			player.qb_updateItem( self.gbIndex, csdefine.QB_ITEM_SKILL, baseItem )
			return True
		elif pyDropped.dragMark == DragMark.QUICK_BAR :
			if self.gbCopy:
				if not baseItem.__class__.__name__ == "CItemBase": return False
				player.qb_updateItem( self.gbIndex, csdefine.QB_ITEM_KITBAG, baseItem )
			else:
				if pyDropped.gbIndex >= csdefine.QB_AUTO_SPELL_INDEX:
					return
				itemID = pyDropped.itemInfo.id
				spaceSkills = player.spaceSkillList
				if itemID in spaceSkills:	#Ϊ�����ռ似��
					if pyTarget.itemInfo is None:
						pyTarget.update( pyDropped.itemInfo )
						pyDropped.update( None )
					else:
						targetID = pyTarget.itemInfo.id
						dropIndex = spaceSkills.index( itemID )
						targetIndex = spaceSkills.index( targetID )
						tempInfo = pyTarget.itemInfo
						pyTarget.update( pyDropped.itemInfo )
						pyDropped.update( tempInfo )
						spaceSkills[dropIndex] = targetID
						spaceSkills[targetIndex] = itemID
					return True
				else:
					index = pyDropped.gbIndex - csdefine.QB_AUTO_SPELL_INDEX		# ��������Ǵ���ģ�����ͨ�� index ���� 0 ���жϸ� item �� AutoFightBar ��� item
					if index < 0 and pyDropped.isNotInit:
						if self.itemInfo and not self.isNotInit:
							ECenter.fireEvent( "EVT_ON_QB_REMOVE_INITE_SKILL", self.itemInfo.id, self.gbIndex )
						player.qb_exchangeItem( pyDropped.gbIndex, self.gbIndex )
						return True
		elif pyDropped.dragMark == DragMark.VEHICLES_PANEL :
			vehicleID = pyDropped.vehicleID
			vehicleData = player.vehicleDatas[vehicleID]
			if vehicleData is None : return
			player.qb_updateItem( self.gbIndex, csdefine.QB_ITEM_VEHICLE, vehicleData )
			return True
		else:
			player.statusMessage( csstatus.QB_ITEM_CANNOT_IN )
			return False

	def onDragStop_( self, pyDragged ) :
		rds.ruisMgr.hideBar.leaveShow()
		rds.ruisMgr.hideBar.hidelightLack()
		rds.ruisMgr.quickBar.hidelightLack()
		if pyDragged.itemInfo is None:return
		player = BigWorld.player()
		dragItemID = pyDragged.itemInfo.id
		if ruisMgr.isMouseHitScreen():
			if not dragItemID in player.spaceSkillList:
				player.qb_removeItem( self.gbIndex )
			if not self.isNotInit:
				ECenter.fireEvent( "EVT_ON_QB_REMOVE_INITE_SKILL", dragItemID, self.gbIndex )
				self.update( None )
				self.pyBinder.removeEffect()

	def onLClick_( self, mods ) :
		pyTopParent = self.pyTopParent
		if self.itemInfo is not None and hasattr( pyTopParent, "isLocked" ) and pyTopParent.isLocked():
			BigWorld.player().statusMessage( csstatus.QB_HAS_LOCKED )
			return False
		Item.onLClick_( self, mods )
		if BigWorld.isKeyDown( KEY_LALT ):
			self.spellItemToSelf()
		else :
			self.spellItem()
		return True
	
	def onMouseLeave_( self ) :
		Item.onMouseLeave_( self )
		toolbox.itemCover.hideItemCover( self )
	
	def onRClick_( self, mods ):
		Item.onRClick_( self, mods )
		self.onLClick_( mods )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def bindShortcut( self, scTag ) :
		shortcutMgr.setHandler( scTag, self.__handleShortcut )

	def bindSelfShortcut( self, scTag ) :
		shortcutMgr.setHandler( scTag, self.__handleSelfShortcut )

	def onEvent( self, macroName, *args ) :
		"""
		triggered by base
		"""
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def clear( self ) :
		"""
		clean the item
		"""
		Item.clear( self )
		self.__pySTAmount.text = ""
		self.__cancelCooldown()
		SKIDetector.unbindPyItem( self )						# ��̽�����Ƴ�

	# -------------------------------------------------
	def checkForDetection_( self, newItemInfo ) :
		"""
		����Ƿ���Ҫ��̽�����и���
		"""
		SKIDetector.unbindPyItem( self )						# ��̽�����еľ��������

		if newItemInfo is None : return

		spell = newItemInfo.getSpell()
		if spell is None : return

		player = BigWorld.player()
		rangeMax = spell.getRangeMax( player )
		rangeMin = spell.getRangeMin( player )

		if rangeMax > 0.0 :
			SKIDetector.bindPyItem( self, ( "COM", rangeMax ) )	# ��ӵ�̽����
		if rangeMin > 0.0 :
			SKIDetector.bindPyItem( self, ( "COM", rangeMin ) )	# ��ӵ�̽����

	def __onMPChanded( self, mp, mpMax ) :
		"""
		written by kebiao
		��ɫMP �ı��֪ͨ�˴�
		"""
		self.updateIconState()

	def __onKigbagChanged( self, itemInfo ):
		"""
		written by kebiao
		���������ɾ����Ʒʱ ��֪ͨ�˴�
		"""
		self.updateIconState()

	def __onActWordChanged( self, oldActWord, newActWord ):
		"""
		written by kebiao
		��ɫactWord�ı� ��֪ͨ�˴�
		"""
		self.updateIconState()

	def __refreshQBItem( self ):
		"""
		ˢ�¿����
		"""
		self.updateIconState()
		
	def __combatCountChanged( self ):
		"""
		�񶷵����ı�
		"""
		self.updateIconState()
		
	def __onENChanged( self, en, enMax ):
		"""
		��Ծֵ�ı�
		"""
		self.updateIconState()
		
	def __onPostureChange( self, posture, oldPosture ):
		"""
		��̬�ı�
		"""
		self.updateIconState()

	def __getReqPotential( self, skillID ):
		"""
		��ҪǱ��
		"""
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		return skillData['ReqPotential']

	def __checkPotential( self, skillID ):
		"""
		Ǳ�ܼ��
		"""
		reqPotential = self.__getReqPotential( skillID )
		return BigWorld.player().potential >= reqPotential

	def __getReqPlayerLevel( self, skillID ):
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		return skillData["ReqLevel"]
	
	def __checkPlayerLevel( self, skillID ):
		"""
		�ȼ����
		"""
		reqPlayerLevel = self.__getReqPlayerLevel( skillID )
		if reqPlayerLevel == 0:return False
		else:
			return BigWorld.player().getLevel() >= reqPlayerLevel
	
	def __getRepSkills( self, skill ):
		"""
		ǰ�ü���˵��
		"""
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if hasattr( skill, "getReqSkills" ):
			player = BigWorld.player()
			reqSkills = skill.getReqSkills()
			for skilID in reqSkills:
				strColor = colorFunc( player.hasSkill( skilID ) )
				skill = Skill.getSkill( skilID )
				skill_level = skill.getLevel()
				skill_name = skill.getName()
				dsp += PL_Font.getSource( " %s"%skill_name+ str( skill_level ) + lbDatas.LEVEL, fc = strColor )
		return dsp

	def updateIconState( self ):
		"""
		written by kebiao
		���¿����ͼ���״̬  ��ɫ,��ɫ
		"""
		player = BigWorld.player()
		itemInfo = self.itemInfo
		indexColor = ( 255, 255, 255, 255 )
		if itemInfo is not None :
			#�����������жϿ�����Ƿ�����
			pyTopParent = self.pyTopParent
			if hasattr( pyTopParent, "isLocked" ) and pyTopParent.isLocked():
				self.color = ( 255, 0, 0, 250 )
				return
			# �����ͼ����ݶԸ���Ʒ���߼��ܶ�Ŀ��ʹ�õ����״̬������ɫ
			state = itemInfo.validTarget()
			if state in [ csstatus.SKILL_GO_ON, csstatus.SKILL_NOT_READY, csstatus.SKILL_ITEM_NOT_READY ]:
				# �������������жϵ��Ⱥ�˳���������
				# �����ܹ��������ʾ���� �����ж��Ѿ��Ϸ���				
				self.color = ( 255, 255, 255, 255 )
			elif player.isDead() or state in [ csstatus.SKILL_NOT_IN_POSTURE, csstatus.SKILL_WEAPON_EQUIP_REQUIRE,\
			csstatus.SKILL_OUTOF_HP,csstatus.SKILL_OUTOF_VITALITY,csstatus.SKILL_OUTOF_MANA,csstatus.SKILL_OUTOF_CombatCount ]:			
				self.color = ( 255, 0, 0, 255 )
				indexColor = ( 255, 0, 0, 255 )			
			else:	#��������ʹ�ü��ܵ�����������ı���ɫ
				indexColor = ( 255, 0, 0, 255 )			
				self.color = ( 255, 255, 255, 255 )	
												
		if self.pyBinder and hasattr(self.pyBinder, "updateIndexColor" ):	#���¼��ܿ�����ֵ���ɫ
			self.pyBinder.updateIndexColor( indexColor )

	def onDetectorTrigger( self ) :
		"""Ŀ��������ص�"""
		self.updateIconState()

	# -------------------------------------------------
	def update( self, itemInfo, isNotInit = True ) :
		self.isNotInit = isNotInit
		self.checkForDetection_( itemInfo )							# ÿ�θ���ǰ�ȼ���Ƿ�Ҫ��ӵ�̽����
		Item.update( self, itemInfo )
		if itemInfo is not None :
			self.__pySTAmount.text = ""
			if itemInfo.countable and itemInfo.amount > 1 :
				self.__pySTAmount.text = str( itemInfo.amount )
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )
			self.focus = isNotInit
			materialFX = "BLEND"
			if not isNotInit:
				materialFX = "COLOUR_EFF"
			self.getGui().materialFX = materialFX
		else :
			self.focus = True
			self.hideAutoParticle()
			self.__pyCDCover.reset( 0 )

	# -------------------------------------------------
	def spellItem( self ) :
		"""
		spell item
		"""
		if self.itemInfo:
			self.itemInfo.spell()

	def spellItemToSelf( self ):
		"""
		����ʹ�÷���
		"""
		if self.itemInfo is not None :
			self.itemInfo.spellToSelf()

	def showAutoParticle( self ):
		"""
		��ʾ�Զ����ܹ�Ч
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__autoParticle ):
			textureName = "maps/particle_2d/guangxiao_huang_kuang/guangxiao_huang_kuang.texanim"
			toolbox.itemParticle.addParticle( self , textureName, self.__autoParticle, 0.99999 )
		else:
			for name, child in gui.children:
				if name == self.__autoParticle:
					child.visible = True
					break

	def hideAutoParticle( self ):
		"""
		�����Զ����ܹ�Ч
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__autoParticle ):
			return
		for name, child in gui.children:
			if name == self.__autoParticle:
				child.visible = False
				break
	
	def startFlash( self ):
		"""
		ͼ����˸ ���뵭��
		"""
		BigWorld.cancelCallback( self.__flashcbid )
		self.__flashcbid = 0
		self.color = ( 255, 255, 255, 255 )
		if self.__flashSign:
			self.__fader.value = 1.0
		else:
			self.__fader.value = 0.2
		self.__flashSign = not self.__flashSign
		self.__flashcbid = BigWorld.callback( self.__fader.speed + 0.1, self.startFlash )
	
	def stopFlash( self ):
		"""
		ֹͣ��˸
		"""
		if self.__flashcbid:
			BigWorld.cancelCallback( self.__flashcbid )
			self.__flashcbid = 0
			self.__fader.value = 1.0
			self.updateIconState()
	
	def isLearnable( self, pLevel ):
		if self.itemInfo is None: return False
		else:
			reqPlayerLevel = self.__getReqPlayerLevel( self.itemInfo.id )
			return reqPlayerLevel <= pLevel
		return False

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getGBIndex( self ) :
		return self.__gbIndex

	def _setGBIndex( self, index ) :
		self.__gbIndex = index

	def _getGBCopy( self ) :
		return self.__gbCopy

	def _setGBCopy( self, isCopy ) :
		self.__gbCopy = isCopy

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGBIndex, _setGBIndex )
	gbCopy =  property( _getGBCopy, _setGBCopy )
