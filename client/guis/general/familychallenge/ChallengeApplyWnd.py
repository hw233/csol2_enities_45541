# -*- coding: gb18030 -*-
#
# ������ս����������� ChallengeApplyWnd
# by gjx 2009-4-13
#

import csconst
from bwdebug import *
from guis import *
from LabelGather import labelGather
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.common.Window import Window
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.RadioButton import RadioButton
from AbstractTemplates import Singleton
import GUIFacade

class ChallengeApplyWnd( Singleton, Window ) :
	__triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/familychallenge/challengeapply.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__gossipTarget = None					# ����Ի�NPC
		self.__trapID = None						# �Ի�����ID

		self.__initialize( wnd )
		self.addToMgr( "ChallengeApplyWnd" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		labelGather.setPyLabel( self.pyLbTitle_, "FamilyChallenge:ChallengeApplyWnd", "lbTitle" )
		self.__pyFamilyName = TextBox( wnd.fNameBox.box )					# Ҫ��ս�ļ�������
		self.__pyFamilyName.inputMode = InputMode.COMMON

		self.__pyRadioGroup = CheckerGroup()						# ������ѡ��ť��
		pyTime = RadioButton( wnd.time_1 )							# ��սʱ�䡪��1Сʱ
		pyTime.time = 1
		self.__pyRadioGroup.addChecker( pyTime )


		pyTime = RadioButton( wnd.time_2 )							# ��սʱ�䡪��2Сʱ
		pyTime.time = 2
		self.__pyRadioGroup.addChecker( pyTime )

		pyTime = RadioButton( wnd.time_3 )							# ��սʱ�䡪��3Сʱ
		pyTime.time = 3
		self.__pyRadioGroup.addChecker( pyTime )

		self.__pyBtnOK = Button( wnd.btnOK )
		self.__pyBtnOK.onLClick.bind( self.__onOK )
		self.__pyBtnOK.setStatesMapping( UIState.MODE_R4C1 )
		self.setOkButton( self.__pyBtnOK )
		labelGather.setPyBgLabel( self.__pyBtnOK, "FamilyChallenge:ChallengeApplyWnd", "btnOK" )

		self.__pyBtnCancel = Button( wnd.btnCancel )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "FamilyChallenge:ChallengeApplyWnd", "btnCancel" )

		self.__pyCostText = StaticText( wnd.costText )				# �ķѵĽ�Ǯ
		labelGather.setPyLabel( self.__pyCostText, "FamilyChallenge:ChallengeApplyWnd", "costText" )

		labelGather.setLabel( wnd.familyPanel.bgTitle.stTitle, "FamilyChallenge:ChallengeApplyWnd", "miFTitle" )
		labelGather.setLabel( wnd.timePanel.bgTitle.stTitle, "FamilyChallenge:ChallengeApplyWnd", "miTTitle" )
		labelGather.setLabel( wnd.time_1.lbText, "FamilyChallenge:ChallengeApplyWnd", "time_1" )
		labelGather.setLabel( wnd.time_2.lbText, "FamilyChallenge:ChallengeApplyWnd", "time_2" )
		labelGather.setLabel( wnd.time_3.lbText, "FamilyChallenge:ChallengeApplyWnd", "time_3" )

	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_FAMILY_CHALLENGE_APPLY"] = SELF.__beginApplyInput
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[ evtMacro ]( *args )

	# --------------------------------------------
	# button about
	# --------------------------------------------
	def __onOK( self ) :
		player = BigWorld.player()
		name = self.__pyFamilyName.text.strip()
		time = self.__pyRadioGroup.pyCurrChecker.time
		if player.family_requestChallenge( name, time ) :
			self.hide()
		print "challenge family:", name, "challengeTime:", time

	def __onCancel( self ) :
		self.hide()

	# --------------------------------------------
	# open window
	# --------------------------------------------
	@classmethod
	def __beginApplyInput( SELF, gossipNPCID ) :
		try :
			gossipNPC = BigWorld.entities[ gossipNPCID ]
		except KeyError :
			ERROR_MSG( "The family challenge application NPC not found!" )
			return
		SELF.inst.show( gossipNPC )

	def __addTrap( self ) :
		"""
		���ڴ򿪺���ӶԻ����壬�������巶Χ�رմ���
		"""
		assert self.__gossipTarget is not None, "The gossip target must not be None!"
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( self.__gossipTarget, "getRoleAndNpcSpeakDistance" ) :
			distance = self.__gossipTarget.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot( self.__gossipTarget.matrix,distance, self.__onEntitiesTrapThrough )

	def __delTrap( self ) :
		"""
		��������ʱȥ���Ի�����
		"""
		if self.__trapID is None: return
		BigWorld.delPot(self.__trapID)
		self.__trapID = None

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_ChallengeApplyWnd :
			INFO_MSG( str( self ) )

	def __onEntitiesTrapThrough( self, isEnter,handle ) :
		"""
		����Ի�NPC���������巶Χ���رմ���
		"""
		if not isEnter :
			self.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onActivated( self ) :
		Window.onActivated( self )
		self.__pyFamilyName.tabStop = True

	def show( self, gossipNPC ) :
		self.__gossipTarget = gossipNPC
		self.__addTrap()
		self.__pyFamilyName.text = ""
		pyDefaultCheck = self.__pyRadioGroup.pyCheckers[0]
		self.__pyRadioGroup.pyCurrChecker = pyDefaultCheck
		Window.show( self )

	def hide( self ) :
		self.__gossipTarget = None
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__delTrap()
		Window.hide( self )
		self.dispose()

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

ChallengeApplyWnd.registerEvents()
