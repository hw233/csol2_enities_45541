# -*- coding: gb18030 -*-
#
# $Id: SkillList.py,v 1.23 2008-08-26 02:19:28 huangyongwei Exp $

"""
implement skilllist window class
"""

import csdefine
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from SkillsPanel import SkillsPanel
from SkillsPanel import LiveSkillsPanel
from Helper import courseHelper
from ItemsFactory import SkillItem
from LabelGather import labelGather
from LivingConfigMgr import LivingConfigMgr
lvcMgr = LivingConfigMgr.instance()

SKILL_TYPE_COMMON	= 0			# ͨ�ü���
SKILL_TYPE_POSTURE1	= 1			# �ķ�һ
SKILL_TYPE_POSTURE2	= 2			# �ķ���
SKILL_TYPE_ACTION	= 3			# ��Ϊ����
SKILL_TYPE_LIVE		= 4			# �����

POSTURE_2_SKILLTYPE = {
	csdefine.ENTITY_POSTURE_NONE 		: ( SKILL_TYPE_COMMON, "skillGeneral" ),		# ͨ��
	csdefine.ENTITY_POSTURE_DEFENCE 	: ( SKILL_TYPE_POSTURE1, "skillDefence" ),		# ����
	csdefine.ENTITY_POSTURE_VIOLENT 	: ( SKILL_TYPE_POSTURE2, "skillViolent" ),		# ��
	csdefine.ENTITY_POSTURE_DEVIL_SWORD	: ( SKILL_TYPE_POSTURE1, "skillDevilSword" ),	# ħ��
	csdefine.ENTITY_POSTURE_SAGE_SWORD 	: ( SKILL_TYPE_POSTURE2, "skillSageSword" ),	# ʥ��
	csdefine.ENTITY_POSTURE_SHOT 		: ( SKILL_TYPE_POSTURE1, "skillShot" ),			# ����
	csdefine.ENTITY_POSTURE_PALADIN 	: ( SKILL_TYPE_POSTURE2, "skillPaladin" ),		# ����
	csdefine.ENTITY_POSTURE_MAGIC 		: ( SKILL_TYPE_POSTURE1, "skillMagic" ),		# ����
	csdefine.ENTITY_POSTURE_CURE 		: ( SKILL_TYPE_POSTURE2, "skillCure" ),			# ҽ��
	}

CLASS_2_POSTURE = {
	csdefine.CLASS_FIGHTER 	: ( csdefine.ENTITY_POSTURE_DEFENCE, csdefine.ENTITY_POSTURE_VIOLENT ),
	csdefine.CLASS_SWORDMAN	: ( csdefine.ENTITY_POSTURE_DEVIL_SWORD, csdefine.ENTITY_POSTURE_SAGE_SWORD ),
	csdefine.CLASS_ARCHER 	: ( csdefine.ENTITY_POSTURE_SHOT, csdefine.ENTITY_POSTURE_PALADIN ),
	csdefine.CLASS_MAGE 	: ( csdefine.ENTITY_POSTURE_MAGIC, csdefine.ENTITY_POSTURE_CURE ),
	}


def _getSkillType( skillInfo ) :
	"""
	��ȡ��������
	"""
	if lvcMgr.isLivingSkill( skillInfo.id ) :
		return SKILL_TYPE_LIVE
	elif skillInfo.id == 1 :
		return SKILL_TYPE_COMMON
	elif skillInfo.isNormalSkill :
		return SKILL_TYPE_ACTION
	else :
		posture = skillInfo.baseItem.getPosture()
		return POSTURE_2_SKILLTYPE[posture][0]


class SkillList( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/skilllist/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__initialize( wnd )

		self.__skillLists = {}
		self.__skillLists[SKILL_TYPE_COMMON] = []
		self.__skillLists[SKILL_TYPE_POSTURE1] = []
		self.__skillLists[SKILL_TYPE_POSTURE2] = []
		self.__skillLists[SKILL_TYPE_ACTION] = []
		self.__skillLists[SKILL_TYPE_LIVE] = []

		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		tabCtrl = wnd.tc
		self.__pyTCSkills = TabCtrl( tabCtrl )
		pnlsClass = 4 * [SkillsPanel] + [ LiveSkillsPanel ]
		self.__pyTCSkills.autoSearchPages( pnlsClass, tabMapMode = UIState.MODE_R3C1 )
		self.__pyPanels = {}
		self.__pyPanels[SKILL_TYPE_COMMON] = self.__pyTCSkills.pyPages[0].pyPanel
		self.__pyPanels[SKILL_TYPE_POSTURE1] = self.__pyTCSkills.pyPages[1].pyPanel
		self.__pyPanels[SKILL_TYPE_POSTURE2] = self.__pyTCSkills.pyPages[2].pyPanel
		self.__pyPanels[SKILL_TYPE_ACTION] = self.__pyTCSkills.pyPages[3].pyPanel
		self.__pyPanels[SKILL_TYPE_LIVE] = self.__pyTCSkills.pyPages[4].pyPanel
		for pyTabBtn in self.__pyTCSkills.pyBtns:
			pyTabBtn.selectedForeColor = ( 142, 216, 217, 255 )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "SkillList:main", "rbTitle" )							# ���＼��
		labelGather.setPyBgLabel( self.__pyTCSkills.pyBtns[0], "SkillList:main", "skillGeneral" )	# ͨ��
		labelGather.setPyBgLabel( self.__pyTCSkills.pyBtns[3], "SkillList:main", "btnAction" )		# ��Ϊ
		labelGather.setPyBgLabel( self.__pyTCSkills.pyBtns[4], "SkillList:main", "btnLive" )		# ����


	# ----------------------------------------------------------------------
	# pravite
	# ----------------------------------------------------------------------
	def __registerTriggers( self ) :
#		self.__triggers["EVT_ON_TOGGLE_SKILL_WINDOW"] = self.__toggleVisible
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] = self.__onAddSkill
		self.__triggers["EVT_ON_PLAYER_POSTURE_CHANGED"] = self.__onPostureChanged					# �����̬�ı�
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = self.__onRemoveSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onUpateSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_NORMAL_SKILL"] = self.__onNormalSkillUpdate
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __toggleVisible( self, tabIndex = None ) :
		if tabIndex is None :
			self.visible = not self.visible
		else :
			pyPages = self.__pyTCSkills.pyPages
			if pyPages.index( self.__pyTCSkills.pySelPage ) == tabIndex :
				self.visible = not self.visible
			else :
				self.__pyTCSkills.pySelPage = pyPages[tabIndex]
				if not self.visible :
					self.show()

	# -------------------------------------------------
	def __onAddSkill( self, skillInfo ) :
		"""
		��Ӽ���
		"""
		skillType = _getSkillType( skillInfo )
		self.__pyPanels[skillType].addSkill( skillInfo )
		self.__skillLists[skillType].append( skillInfo.id )

	def __onRemoveSkill( self, skillInfo ) :
		"""
		ɾ������
		"""
		skillType = _getSkillType( skillInfo )
		skillIDs = self.__skillLists[skillType]
		skillID = skillInfo.id
		if skillID in skillIDs :
			self.__pyPanels[skillType].removeSkill( skillID )
			skillIDs.remove( skillID )

	def __onUpateSkill( self, oldSkillID, skillInfo ) :
		"""
		���¼���
		"""
		skillType = _getSkillType( skillInfo )
		skillIDs = self.__skillLists[skillType]
		if oldSkillID in skillIDs :
			self.__pyPanels[skillType].updateSkill( oldSkillID, skillInfo )
			skillIDs.remove( oldSkillID )
			skillIDs.append( skillInfo.id )

	def __onNormalSkillUpdate( self, skillID, baseItem ) :
		"""
		������ͨ����������
		"""
#		skillType = SKILL_TYPE_ACTION
		skillType = SKILL_TYPE_COMMON
		skillIDs = self.__skillLists[skillType]
		skillInfo = SkillItem( baseItem )
		if skillID in skillIDs:
			self.__pyPanels[skillType].updateSkill( skillID, skillInfo )

	def __setPostureLabels( self ) :
		"""
		���ݽ�ɫ��ְҵ���ý������
		"""
		postures = CLASS_2_POSTURE[ BigWorld.player().getClass() ]
		pyTBtns = [ self.__pyTCSkills.pyBtns[1], self.__pyTCSkills.pyBtns[2] ]
		for idx, pyBtn in enumerate( pyTBtns ) :
			pText = POSTURE_2_SKILLTYPE[ postures[idx] ][1]
			labelGather.setPyBgLabel( pyBtn, "SkillList:main", pText )

	def __onPostureChanged( self, newPosture, oldPosture ) :
		"""
		�����̬�ı�
		"""
		self.__pyPanels[SKILL_TYPE_POSTURE1].refreshSkills()
		self.__pyPanels[SKILL_TYPE_POSTURE2].refreshSkills()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()
		for skType in self.__skillLists :
			self.__skillLists[skType] = []
		for pyPanel in self.__pyPanels.itervalues() :
			pyPanel.clearItems()

	def onEnterWorld( self ) :
		Window.onEnterWorld( self )
		self.__setPostureLabels()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		Window.show( self )
		self.__pyTCSkills.pySelPage.pyPanel.show()
		rds.helper.courseHelper.openWindow( "jineng_chuangkou" )

	def hide( self ) :
		Window.hide( self )
