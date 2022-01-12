# -*- coding: gb18030 -*-
#
# $Id: SkillTrainer.py,v 1.41 2008-09-05 06:11:34 fangpengjun Exp $

"""
implement StuffProcessor window class
"""
import csconst
import csdefine
from guis import *
import GUIFacade
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ListPanel import ListPanel
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.StaticText import StaticText
from guis.controls.StaticLabel import StaticLabel
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from SkillItem import SkillItem
from SkillInfo import SkillInfo
from LabelGather import labelGather
from config.client.labels.ItemsFactory import POSTURE_STR
from guis.OpIndicatorObj import OpIndicatorObj

class SkillTrainer( UnfixedTrapWindow, OpIndicatorObj ) :
	__cg_item = None

	def __init__( self ) :
		wnd = GUI.load( "guis/general/skilltrainer/window.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )
		OpIndicatorObj.__init__( self )
		if SkillTrainer.__cg_item is None :
			SkillTrainer.__cg_item = GUI.load( "guis/general/skilltrainer/skillitem.gui" )

		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.sortByLevelFlag 	= 0		# ���ȼ�����ı��
		self.sortByNameFlag 	= 0		# ��ְҵ����ı��
		self.__preTaxisType		= -1 	# -1��ʾ���û��ѡ�������0��ʾ�ϴΰ��ȼ�����1�ǰ���������
		self.__pyItems = []
		self.trainer = None
		self.trainerName = ""				# ��¼��ǰ����NPC����
		self.__triggers = {}
		self.__registerTriggers()
		self.__callbackID = 0

		self.__defaultColor = ( 255, 255, 255, 255 )

	def __initialize( self, wnd ) :
		self.__pyLPSkills = ListPanel( wnd.skillPanel.clipPanel, wnd.skillPanel.sbar )
		self.__pyLPSkills.onItemSelectChanged.bind( self.__onSkillItemSelectedChanged )

		self.__pyTPDsp = ItemsPanel( wnd.dspPanel.clipPanel, wnd.dspPanel.sbar )

		self.__pyCBFilter = ODComboBox( wnd.cbFilter )
		self.__pyCBFilter.autoSelect = False
		self.__pyCBFilter.ownerDraw = True
		self.__pyCBFilter.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBFilter.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBFilter.onItemSelectChanged.bind( self.__onFilterChanged )
		self.__pyCBFilter.pyBox_.foreColor = ( 255.0, 241.0, 192.0, 255.0 )
		self.__initFilter()

		self.__pyNameBtn = Button( wnd.nameBtn )
		self.__pyNameBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyNameBtn.onLClick.bind( self.__taxisByName )

		self.__pyLevelBtn = Button( wnd.levelBtn )
		self.__pyLevelBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyLevelBtn.onLClick.bind( self.__taxisByLevel )
		self.__pyLevelBtn.foreColor = ( 255, 248, 158, 255 )

		self.__pyLeranBtn = Button( wnd.learnBtn )
		self.__pyLeranBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyLeranBtn.onLClick.bind( self.__learnSkill )
		self.__pyLeranBtn.enable = False

		self.__pyLbPotential = StaticText( wnd.lbPotential )
		self.__pyLbPotential.text = ""

		self.__skillInfo = SkillInfo()
		self.__skillInfo.visible = False
		self.__pyTPDsp.addItem( self.__skillInfo )

		self.__dspRichText = CSRichText()
		self.__dspRichText.maxWidth = self.__pyTPDsp.width
		self.__dspRichText.text = ""

		self.__pyTPDsp.addItem( self.__dspRichText )
		self.__pyTPDsp.wholeLen = self.__dspRichText.bottom
		self.__pyTPDsp.perScroll = 20.0

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "SkillTrainer:main", "rbTitle" )					# ����ѧϰ
		labelGather.setPyBgLabel( self.__pyNameBtn, "SkillTrainer:main", "btnSkillName" )	# ��������
		labelGather.setPyBgLabel( self.__pyLeranBtn, "SkillTrainer:main", "btnLearn" )		# ѧϰ

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		pyLabel.text = pyViewItem.listItem

	def __initFilter( self ) :
		enableSkill = labelGather.getText( "SkillTrainer:main", "miAbleSkill" )
		unableSkill = labelGather.getText( "SkillTrainer:main", "miUnableSkill" )
		allSkill = labelGather.getText( "SkillTrainer:main", "miAllSkill" )
		self.__pyCBFilter.addItems( [enableSkill, unableSkill, allSkill] )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.__triggers["EVT_ON_SHOW_LEARN_SKILL_WINDOW"] = self.show
		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotenChanged
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_CONTRIBUTE"] = self.__onContributeChange	 	# ��ṱ�׶ȸı�
		self.__triggers["EVT_ON_VEHICLE_SKPOINT_UPDATE"] = self.__onVehicleSKPointChanged 		# ��ṱ�׶ȸı�
		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onMountingVehicle					# ����
		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onOffVehicle						# ����
		self.__triggers["EVT_ON_SKILL_LEARNT"] = self.__onSkillLearnt
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] = self.__onRoleAddSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onUpateSkill
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.__hide										# ��ɫ���������ش���
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------
	def __createSkillItem( self, skill ) :
		pyItem = None
		if len( self.__pyItems ) > 0 :
			pyItem = self.__pyItems.pop( 0 )
		item = util.copyGuiTree( SkillTrainer.__cg_item )
		uiFixer.firstLoadFix( item )
		pyItem = SkillItem( item )
		pyItem.skill = skill
		if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			pyItem.text = skill.getName() + '(' + str( skill.getLevel() ) +')' + labelGather.getText( "SkillTrainer:main", "miPassive" )
		else:
			pyItem.text = skill.getName() + '(' + str( skill.getLevel() ) +')'
		if self.trainerName == "VehicleTrainer" :
			pyItem.level = skill.getNeedVehicleLevel()
		else :
			pyItem.level = skill.getNeedPlayerLevel()
		pyItem.name = skill.getName()
		self.__renderItem( pyItem )
		pyItem.onStateChanged_( UIState.COMMON )
		return pyItem

	def __renderItem( self, pyItem ) :
		skill = pyItem.skill
		if not skill.learnable() :
			pyItem.commonForeColor = ( 255, 10, 10, 255 )
			pyItem.highlightForeColor = ( 255, 10, 10, 255 )
			pyItem.selectedForeColor = ( 255, 10, 10, 255 )
		else :
			pyItem.commonForeColor = ( 96, 224, 103, 255 )
			pyItem.highlightForeColor = ( 96, 224, 103, 255 )
			pyItem.selectedForeColor = ( 96, 224, 103, 255 )

	# ---------------------------------------
	def __showAllSkills( self ) :
		skills = GUIFacade.getLearnSkills()
		for index, skill in enumerate( skills ) :
			if not skill.getSkill().checkMetier():continue
			if skill.getSkill().islearnMax( self.trainer ) : continue
			pyItem = self.__createSkillItem( skill )
			self.__pyLPSkills.addItem( pyItem )

	def __showLearnableSkills( self ) :
		skills = GUIFacade.getLearnSkills()
		for index, skill in enumerate( skills ) :
			if not skill.learnable() : continue
			pyItem = self.__createSkillItem( skill )
			self.__pyLPSkills.addItem( pyItem )

	def __showUnlearnableSkills( self ) :
		skills = GUIFacade.getLearnSkills()
		for index, skill in enumerate( skills ) :
			if not skill.getSkill().checkMetier():continue
			if skill.learnable() : continue
			pyItem = self.__createSkillItem( skill )
			self.__pyLPSkills.addItem( pyItem )

	# -------------------------------------------------
	def __onFilterChanged( self, selIndex ) :
		if selIndex < 0:return
		self.__pyLPSkills.clearItems()
		if selIndex == 0 : self.__showLearnableSkills()
		elif selIndex == 1 : self.__showUnlearnableSkills()
		elif selIndex == 2 : self.__showAllSkills()
		self.__pyCBFilter.pyBox_.text = self.__pyCBFilter.selItem

	def __onSkillItemSelectedChanged( self, pyItem ) :
		"""
		"""
		self.__pyLeranBtn.enable = pyItem is not None
		if pyItem:
			skill = pyItem.skill
			self.__skillInfo.visible = True
			self.__skillInfo.updateInfo( skill )
			#COLOUR_GREEN	= ( 0, 255, 0, 255 )
			#COLOUR_RED 		= ( 255, 0, 0, 255 )
			space2 = PL_Space.getSource( 2 )
			newLine = PL_NewLine.getSource()
			dsp_text = ""

			# �ķ�����
			needPosture = skill.getLearnSkill().getPosture()
			if needPosture != csdefine.ENTITY_POSTURE_NONE :
				postureStr = POSTURE_STR.get( needPosture, "Unknown posture" )
				postureStr = PL_Font.getSource( postureStr )
#				postureStr = PL_Font.getSource( postureStr, fc = ( 255, 255, 0, 255 ) )
				dsp_text += space2 + postureStr + newLine

			# ��������
			require = skill.getRequire()
			tem_text = ""
			if require is not None:
				tem_text = require.getRequireManaDscription( skill.getSkill() )
			if tem_text != "":
				tem_text = space2 + tem_text
				tem_text = PL_Font.getSource( tem_text, fc = ( 230, 227, 185, 255 ) )
			dsp_text += tem_text

			# ��Ҫ��Ʒ
			tem_text = ""
			if require is not None:
				tem_text = skill.getRequire().getRequireItemDscription( skill.getSkill() )
			if tem_text != "":
				tem_text = space2 + labelGather.getText( "SkillTrainer:main", "miNeedItem", tem_text )
				tem_text = PL_Font.getSource( tem_text, fc = ( 230, 227, 185, 255 ) )
			dsp_text += tem_text

			# ����˵��
			tem_text = labelGather.getText( "SkillTrainer:main", "miSkillInfo", newLine, space2, skill.getDescription() )
			tem_text = PL_Font.getSource( tem_text, fc = ( 230, 227, 185, 255 ) )
			dsp_text += tem_text

			# ��Ҫǰ�ü���
			tem_text = skill.getRepSkill()
			if tem_text != "":
				tem_text = labelGather.getText( "SkillTrainer:main", "miFrontSkill", newLine, tem_text )
				if skill.checkPremissSkill():
					tem_text = PL_Font.getSource( tem_text, fc = ( 0, 255, 0 ) )
				else:
					tem_text = PL_Font.getSource( tem_text, fc = ( 255, 0, 0 ) )
			dsp_text += tem_text

			if skill.isTongSkill():#��Ἴ��
				tem_text = labelGather.getText( "SkillTrainer:main", "miNeedContribute", newLine, space2, skill.reqTongContribute() )
				if skill.checkTongContribute():
					tem_text = PL_Font.getSource( tem_text, fc = ( 0, 255, 0 ) )
				else:
					tem_text = PL_Font.getSource( tem_text, fc = ( 255, 0, 0 ) )
				dsp_text += tem_text
			else:
				spText = ""
				if self.trainerName == "Trainer" or self.trainerName == "EidolonNPC":					# ��ɫ���ܵ�ʦ
					spText = labelGather.getText( "SkillTrainer:main", "miNeedPoteneial", newLine, space2, skill.getPotential() )
					lvText = labelGather.getText( "SkillTrainer:main", "miNeedLevel", newLine, space2, skill.getLearnLevel() )
				elif self.trainerName == "VehicleTrainer" :			# ��輼�ܵ�ʦ
					spText = labelGather.getText( "SkillTrainer:main", "miNeedTSkill", newLine, space2, skill.getPotential() )
					lvText = labelGather.getText( "SkillTrainer:main", "miNeedTLevel", newLine, space2, skill.getLearnLevel() )
				if skill.checkPotential():
					tem_text = PL_Font.getSource( spText, fc = ( 0, 255, 0 ) )
				else:
					tem_text = PL_Font.getSource( spText, fc = ( 255, 0, 0 ) )
				dsp_text += tem_text

				# ��Ҫ�ȼ�
				if skill.checkLevel():
					tem_text = PL_Font.getSource( lvText, fc = ( 0, 255, 0 ) )
				else:
					tem_text = PL_Font.getSource( lvText, fc = ( 255, 0, 0 ) )
				dsp_text += tem_text

			self.__dspRichText.text = dsp_text
		else:
			self.__skillInfo.updateInfo( None )
			self.__dspRichText.text = ""
			self.__skillInfo.visible = False
		self.__pyTPDsp.wholeLen = self.__dspRichText.bottom
	
	def __onRoleAddSkill( self, skillInfo ):
		"""
		������Ӽ��ܣ���Ҫɾ����ѧ����
		"""
		if self.trainerName != "Trainer":return
		if skillInfo is None:return
		skillID = skillInfo.id
		for pyItem in self.__pyLPSkills.pyItems:
			skill = pyItem.skill
			if skill is None:continue
			spellTeachID = skill.getSpellTeachID()
			if skillID == spellTeachID:							#��1������
				self.__pyLPSkills.removeItem( pyItem )
				
	def __onUpateSkill( self, oldSkID, skillInfo ):
		"""
		ֻ�е�ǰ����ѧϰ�ɹ�֮�󣬲�����ѧϰ��һ���ܣ���ֹ������죬�������˺Ϳͻ��˲�ͬ������
		"""
		if self.trainerName == "Trainer" \
		or self.trainerName == "TongTrainer" or self.trainerName == "EidolonNPC":
			if skillInfo is None:return
			self.__pyLeranBtn.enable = oldSkID != skillInfo.id

	def __setLearnBtn( self ):
		if not self.__pyLeranBtn.enable:
			self.__pyLeranBtn.enable = True
		BigWorld.cancelCallback( self.__callbackID )

	def __taxisByName( self ): # �����������������б�
		flag = self.sortByNameFlag and True or False
		self.__pyLPSkills.sort( key = lambda n: n.name, reverse = flag )
		self.sortByNameFlag = not self.sortByNameFlag
		self.__preTaxisType = 1

	def __taxisByLevel( self ): # �����ܵȼ��������б�
		flag = self.sortByLevelFlag and True or False
		self.__pyLPSkills.sort( key = lambda n: n.level, reverse = flag )
		self.sortByLevelFlag = not self.sortByLevelFlag
		self.__preTaxisType = 0

	def __getLearnableSkillsID( self ):
		IDL = []
		skills = GUIFacade.getLearnSkills()
		for skill in skills :
			if skill.learnable() :
				IDL.append( skill.getID() )
		return IDL

	def __learnSkill( self ) :
		pyItem = self.__pyLPSkills.pySelItem
		if pyItem is None :
			return
		GUIFacade.learnSkill( pyItem.skill )
		self.__pyLeranBtn.enable = False
		if self.trainerName == "TongTrainer":
			self.__callbackID = BigWorld.callback( 1.0, self.__setLearnBtn ) #�����1���ѧϰ��ťû�и�λ������ѧϰ���ɹ���������û�з���,���ֶ���λ
		self.clearIndications()

	def __hide( self ):
		self.hide()

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:
			self.__hide()														#���ص�ǰ����ѵ������

	def __onResolutionChanged( self, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		for pyItem in self.__pyItems :
			uiFixer.fix( preReso, pyItem.getGui() )

	def __onRolePotenChanged( self, oldValue, newValue ): #��ͨNPC��ʾǱ��
		if self.trainerName == "Trainer" or self.trainerName == "EidolonNPC":
			self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miPotential", newValue )

	def __onContributeChange( self, memberID, contribute ): #��Ἴ��NPC��ʾ��ṱ�׶�
		player = BigWorld.player()
		if player.databaseID == memberID and self.trainerName == "TongTrainer":
			self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miContribute", contribute )

	def __onVehicleSKPointChanged( self, dbid ):
		"""
		��輼�ܵ����
		"""
		if not self.visible : return								# ���治�ɼ�
		if self.trainerName != "VehicleTrainer" : return			# ������赼ʦѧϰ����
		player = BigWorld.player()
		if dbid != player.vehicleDBID : return						# ���ǵ�ǰ���
		skPoint = player.vehicleDatas[dbid]["skPoint"]
		self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miVehicleSkill", skPoint )
		pyItemsec = self.__pyLPSkills.pySelItem
		self.__onSkillItemSelectedChanged( pyItemsec )

	def __onMountingVehicle( self ) :
		if not self.visible : return								# ���治�ɼ�
		if self.trainerName != "VehicleTrainer" : return			# ������赼ʦѧϰ����
		player = BigWorld.player()
		skPoint = player.vehicleDatas[player.vehicleDBID]["skPoint"]
		self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miVehicleSkill", skPoint )
		pyItemsec = self.__pyLPSkills.pySelItem
		self.__onSkillItemSelectedChanged( pyItemsec )
		# ����ܷ�ѧϰ��輼�ܵ��ж��뵱ǰ�Ƿ����������޹أ���
		# ����ĸ����ǲ���Ҫ�ġ�
		selIndex = self.__pyCBFilter.selIndex
		self.__onFilterChanged( selIndex )

	def __onOffVehicle( self ) :
		if not self.visible : return								# ���治�ɼ�
		if self.trainerName != "VehicleTrainer" : return			# ������赼ʦѧϰ����
		self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miUnVehicle" )
		# ����ܷ�ѧϰ��輼�ܵ��ж��뵱ǰ�Ƿ����������޹أ���
		# ����ĸ����ǲ���Ҫ�ġ�
		selIndex = self.__pyCBFilter.selIndex
		self.__onFilterChanged( selIndex )

	# -------------------------------------------------
	def __onSkillLearnt( self, skillID ) :
		pyItems = self.__pyLPSkills.pyItems
		selIndex = self.__pyCBFilter.selIndex
		learnableSID = self.__getLearnableSkillsID()
		for pyItem in pyItems :
			skill = pyItem.skill
			SID = skill.getID()
			self.__renderItem( pyItem )
			if SID in learnableSID :
				learnableSID.remove( SID )
			if SID != skillID : continue
			if self.trainerName != "VehicleTrainer":
				self.__pyLPSkills.removeItem( pyItem )		
						
			if self.trainerName == "VehicleTrainer" :
				pyItem.level = skill.getNeedVehicleLevel()
			else :
				pyItem.level = skill.getNeedPlayerLevel()
			pyItem.text = skill.getName() + '(' + str( skill.getLevel() ) +')'
			if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
				pyItem.text += labelGather.getText( "SkillTrainer:main", "miPassive" )

		if learnableSID:
			for ID in learnableSID :
				skill = GUIFacade.LearningSkill( ID )
				pyItem = self.__createSkillItem( skill )
				self.__pyLPSkills.addItem( pyItem )
			if self.__preTaxisType == 0 :									# �ϴΰ��ȼ�����
				self.sortByLevelFlag = not self.sortByLevelFlag
				self.__taxisByLevel()
			elif self.__preTaxisType == 1 :									# �ϴΰ���������
				self.sortByNameFlag = not self.sortByNameFlag
				self.__taxisByName()

		pyItemsec = self.__pyLPSkills.pySelItem
		self.__onSkillItemSelectedChanged( pyItemsec )

	def __onServerNotify( self ):
		selIndex = self.__pyLPSkills.selIndex
		self.__pyLPSkills.clearItems()
		index = self.__pyCBFilter.selIndex
		if index == 0 : self.__showLearnableSkills()
		elif index == 1 : self.__showUnlearnableSkills()
		elif index == 2 : self.__showAllSkills()
		if selIndex > 0:
			self.__pyLPSkills._setSelIndex( selIndex )

	def onMove_( self, dx, dy ) :
		UnfixedTrapWindow.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0081 )
#		toolbox.infoTip.moveOperationTips( 0x0082 )
		self.relocateIndications()

	# ----------------------------------------------------------------
	# operate indication methods
	# ----------------------------------------------------------------
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","skillTrainer" )
		condition = ( "talking_npc","quest_uncompleted", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndicationBindToButton

	def __showIndicationBindToButton( self, idtId, skillID ) :
		"""
		"""
		if self.__pyLeranBtn.rvisible :
			toolbox.infoTip.showHelpTips( idtId, self.__pyLeranBtn )
			self.addVisibleOpIdt( idtId )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.__pyLPSkills.clearItems()
		self.__skillInfo.visible = False
		self.__dspRichText.text = ""
		self.trainerName = ""
		self.trainer = None
		self.__pyLeranBtn.enable = False
		self.hide()

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def hide( self ):
		UnfixedTrapWindow.hide( self )
		toolbox.infoTip.hideOperationTips( 0x0081 )
		toolbox.infoTip.hideOperationTips( 0x0082 )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.clearIndications()
		if self.trainer and BigWorld.player().isLearnSkillQuestCompleted():
			GUIFacade.gossipHello( self.trainer )

	def show( self, trainer ) :
		player = BigWorld.player()
		self.trainer = trainer
		self.trainerName = trainer.__class__.__name__ #��ȡ�Ի����ܵ�ʦ��
		self.__preTaxisType == -1
		self.__pyCBFilter.selIndex = 0
		selIndex = self.__pyCBFilter.selIndex
		self.__onFilterChanged( selIndex )
		# ���ݵ�ʦ���͸�����Ӧ�Ľ������
		if self.trainerName == "Trainer" or self.trainerName == "EidolonNPC":
			self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miPotential", player.potential )
			self.__pyLevelBtn.text = labelGather.getText( "SkillTrainer:main", "miNeedSLevel" )
		elif self.trainerName == "TongTrainer":
			databaseID = player.databaseID
			playerMember = player.tong_memberInfos.get( databaseID ) #��ȡ�Լ��ڰ���Ա��Ϣ
			if playerMember is None:return
			self.__pyLbPotential.text = labelGather.getText( "SkillTrainer:main", "miContribute", playerMember.getContribute() )
			levelBtnText = ""
			if trainer.skillType == csdefine.TONG_SKILL_ROLE: #��ɫ��Ἴ�ܵȼ�
				levelBtnText = labelGather.getText( "SkillTrainer:main", "miNeedSLevel" )
			else:
				levelBtnText = labelGather.getText( "SkillTrainer:main", "miNeedPSLevel" )
			self.__pyLevelBtn.text = levelBtnText
		elif self.trainerName == "VehicleTrainer" :
			if player.vehicleDBID:
				vehicleData = player.vehicleDatas.get( player.vehicleDBID )
				if vehicleData:
					skPoint = vehicleData["skPoint"]
					text = labelGather.getText( "SkillTrainer:main", "miVehicleSkill", skPoint )
			else :
				text = labelGather.getText( "SkillTrainer:main", "miUnVehicle" )
			self.__pyLbPotential.text = text
			self.__pyLevelBtn.text = labelGather.getText( "SkillTrainer:main", "miNeedTSLevel" )
		self.setTrappedEntID( trainer.id )
		UnfixedTrapWindow.show( self )
#		toolbox.infoTip.showOperationTips( 0x0081, self.__pyLPSkills )
#		if self.__pyLPSkills.pySelItem:
#			toolbox.infoTip.showOperationTips( 0x0082, self.__pyTPDsp )

		rds.helper.courseHelper.interactive( "Trainer" )
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","skillTrainer" ) )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setPos( self, ( left, top ) ) :
		UnfixedTrapWindow._setPos( self, ( left, top ) )
#		toolbox.infoTip.moveOperationTips( 0x0081 )
#		toolbox.infoTip.moveOperationTips( 0x0082 )
		self.relocateIndications()

	pos = property( UnfixedTrapWindow._getPos, _setPos )