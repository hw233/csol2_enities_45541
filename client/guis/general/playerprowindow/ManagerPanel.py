# -*- coding: gb18030 -*-
#
# $Id: GemManagePanel.py, fangpengjun Exp $
#
from bwdebug import *
from guis import *
from LabelGather import labelGather
from guis.controls.ListPanel import ListPanel
from guis.controls.TabCtrl import TabPanel
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.StaticText import StaticText
from guis.common.PyGUI import PyGUI
#from PetFormulas import formulas
import csdefine
import csstatus

class GemManagePanel( TabPanel ):
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyPlayerGem = PlayerGem( tabPanel.playerGem )
		self.__pyPetGem = PetGem( tabPanel.petGem )

		self.__pyStPoint = StaticText( tabPanel.stPoint )
		self.__pyStPoint.text = ""
		labelGather.setLabel( tabPanel.remainPointText, "PlayerProperty:GemPanel", "remainGold" )

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onGoldChanged 		# ��Ԫ�����������仯
		self.__triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self.__onSilverChanged	# ��Ԫ�����������仯
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------------------------
	def __onGoldChanged( self, oldGold, newGold ):
		self.__pyStPoint.text = str( newGold )

	def __onSilverChanged( self, oldGold, newGold ):
		"""
		��Ԫ���仯
		"""
		DEBUG_MSG( "---->>>oldGold:%i,newGold:%i." % ( oldGold, newGold ) )

	def reset( self ):
		self.__pyPlayerGem.reset()
		self.__pyPetGem.reset()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

# -------------------------------------------------------
class GemManage( PyGUI ): #��ʯ�������

	def __init__( self, gemPanel ):
		PyGUI.__init__( self, gemPanel )
		self.triggers_ = {}
		self.registerTriggers_()
		self.__initpanel( gemPanel )

	def __initpanel( self, panel ):
		self.pyBtnTrain_ = Button( panel.btnTraining ) #����
		self.pyBtnTrain_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnTrain_, "PlayerProperty:GemPanel", "btnTraining")

		self.pyBtnAsTrain_ = Button( panel.btnAssidTrain ) #�̿����
		self.pyBtnAsTrain_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnAsTrain_, "PlayerProperty:GemPanel", "btnAssidTrain")

		self.pyBtnPause_ = Button( panel.btnPauseTrain ) #��ֹ����
		self.pyBtnPause_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnPause_, "PlayerProperty:GemPanel", "btnPauseTrain")

		self.pyBtnCharge_ = Button( panel.btnCharge ) #��ֵ
		self.pyBtnCharge_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCharge_.enable = False
		labelGather.setPyBgLabel( self.pyBtnCharge_, "PlayerProperty:GemPanel", "btnCharge")

		self.pyStCurExp_ = StaticText( panel.stCurExp ) #��ǰ����
		self.pyStCurExp_.text = ""

		self.pyCurState_ = StaticText( panel.stCurState ) #��ǰ״̬
		self.pyCurState_.text = ""

		self.pyStRemainTime_ = StaticText( panel.stRemainTime ) #ʣ��ʱ��
		self.pyStRemainTime_.text = ""

		self.pyStUnit_ = StaticText( panel.stUnit ) #ÿСʱ����Ԫ����
		self.pyStUnit_.text = ""

		self.pyRtWarning_ = CSRichText( panel.rtWarning )
		self.pyRtWarning_.text = PL_Font.getSource( labelGather.getText( "PlayerProperty:GemPanel", "warnText" ), fc = ( 255, 73, 24, 255 ) )

		self.pyChargeBox_ = TextBox( panel.chargeBox.box ) #��ֵ��
		self.pyChargeBox_.inputMode = InputMode.INTEGER
		self.pyChargeBox_.filterChars = ['-', '+']
		self.pyChargeBox_.maxLength = 5
		self.pyChargeBox_.onTextChanged.bind( self.__onTextChange )
		self.pyChargeBox_.text = ""
		labelGather.setLabel( panel.hoursText, "PlayerProperty:GemPanel", "hourText" )
		labelGather.setLabel( panel.curExpText, "PlayerProperty:GemPanel", "curExpText" )
		labelGather.setLabel( panel.curStatusText, "PlayerProperty:GemPanel", "curStatusText" )
		labelGather.setLabel( panel.remainTimeText, "PlayerProperty:GemPanel", "remainText" )
		labelGather.setLabel( panel.explainText0, "PlayerProperty:GemPanel", "eachText" )
		labelGather.setLabel( panel.explainText1, "PlayerProperty:GemPanel", "exchangeText" )
		labelGather.setLabel( panel.chargeTimeText, "PlayerProperty:GemPanel", "chargeText" )

	# -----------------------------------------------------------
	# pravite
	# -----------------------------------------------------------
	def registerTriggers_( self ):
		pass
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	def __onTextChange( self ):
		enable = self.pyChargeBox_.text != "" and  not self.pyChargeBox_.text.startswith( "0" )
		self.pyBtnCharge_.enable = enable

	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.triggers_[eventMacro]( *args )

	def reset( self ):
		self.pyStCurExp_.text = ""
		self.pyCurState_.text = ""
		self.pyStRemainTime_.text = ""
		self.pyChargeBox_.text = ""

# -----------------------------------------------------------------
# ��ɫ��ʯ����
# -----------------------------------------------------------------
class PlayerGem( GemManage ): #��ұ�ʯ����
	def __init__( self, gemPanel ):
		GemManage.__init__( self, gemPanel )
		self.pyBtnTrain_.onLClick.bind( self.__onPlayerTrain )

		self.pyBtnDistill_ = Button( gemPanel.btnDistill ) #��ȡ����
		self.pyBtnDistill_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnDistill_.onLClick.bind( self.__onPlayerDisExp )
		labelGather.setPyBgLabel( self.pyBtnDistill_, "PlayerProperty:GemPanel", "btnDistill")

		self.pyBtnAsTrain_.onLClick.bind( self.__onPlayerAsTrain )
		self.pyBtnPause_.onLClick.bind( self.__onPlayerPauseTrain )
		self.pyBtnCharge_.onLClick.bind( self.__onPlayerCharge )

		self.pyStUnit_.text = "20"
		labelGather.setLabel( gemPanel.bgTitle.stTitle, "PlayerProperty:GemPanel", "roleUpgrade" )

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_PLAYER_TRAIN_TYPE_CHANGED"]				= self.__onTrainTypeChange
		self.triggers_["EVT_ON_PLAYER_REMAIN_TRAIN_TIME_CHANGED"]		= self.__onTrainTimeChange
#		self.triggers_["EVT_ON_PLAYER_REMAIN_TRAIN_POINT_CHANGED"] 		= self.__onTrainPointChange
		self.triggers_["EVT_ON_PLAYER_TRAIN_EXP_CHANGED"]				= self.__onExpChange
		GemManage.registerTriggers_( self )

	# ------------------------------------------------------------
	def __onTrainTypeChange( self, type ):
		if type == csdefine.GEM_WORK_NORMAL:
			self.pyBtnTrain_.enable = False
			self.pyBtnAsTrain_.enable = True
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "comUpgrade" )
		elif type == csdefine.GEM_WORK_HARD:
			self.pyBtnTrain_.enable = True
			self.pyBtnAsTrain_.enable = False
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "hardUpgrade" )
		else:
			self.pyBtnTrain_.enable = True
			self.pyBtnAsTrain_.enable = True
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "notUpgrade" )

	def __onTrainTimeChange( self, time ):
		hours = time / 3600
		minutes = ( time % 3600 )/60
		self.pyStRemainTime_.text = labelGather.getText( "PlayerProperty:GemPanel", "remainTime" )%( hours, minutes )

	def __onExpChange( self, exp ):
		self.pyStCurExp_.text = labelGather.getText( "PlayerProperty:GemPanel", "expPoint" )%int(exp)

	def __onPlayerTrain( self ): #��ͨ����
		BigWorld.player().gem_startTrain( csdefine.GEM_WORK_NORMAL )

	def __onPlayerAsTrain( self ): #�̿����
		BigWorld.player().gem_startTrain( csdefine.GEM_WORK_HARD )

	def __onPlayerDisExp( self ): #��ȡ����
		BigWorld.player().gem_derive()

	def __onPlayerPauseTrain( self ): #
		BigWorld.player().gem_stopTrain()

	def __onPlayerCharge( self ):
		time = int( self.pyChargeBox_.text )
		gold = time*int( self.pyStUnit_.text )
		player = BigWorld.player()
		if player.gold < gold:
			player.statusMessage( csstatus.PET_TRAIN_CHARGE_FAIL_LACK_GOLD )
			return
		player.base.gem_charge( gold )
		self.pyChargeBox_.text = ""

	def reset( self ):
		trainGem = BigWorld.player().roleTrainGem
		trainGem.stopUpdateTimer()
		GemManage.reset( self )

# ----------------------------------------------------------
# ���ﱦʯ����
# ----------------------------------------------------------
class PetGem( GemManage ): #���ﱦʯ����
	def __init__( self, gemPanel ):
		GemManage.__init__( self, gemPanel )

		self.pyBtnTrain_.onLClick.bind( self.__onPetTrain )
		self.pyBtnAsTrain_.onLClick.bind( self.__onPetAsTrain )
		self.pyBtnPause_.onLClick.bind( self.__onPetPauseTrain )
		self.pyBtnCharge_.onLClick.bind( self.__onPetCharge )

		self.pyStUnit_.text = "20"
		labelGather.setLabel( gemPanel.bgTitle.stTitle, "PlayerProperty:GemPanel", "petUpgrade" )

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_PET_TRAIN_TYPE_CHANGED"]				= self.__onTrainTypeChange
		self.triggers_["EVT_ON_PET_REMAIN_TRAIN_TIME_CHANGED"]		= self.__onTrainTimeChange
#		self.triggers_["EVT_ON_PET_REMAIN_TRAIN_POINT_CHANGED"] 	= self.__onTrainPointChange
		self.triggers_["EVT_ON_PET_TRAIN_EXP_CHANGED"]				= self.__onExpChange
		GemManage.registerTriggers_( self )

	# ----------------------------------------------------------------------------
	def __onTrainTypeChange( self, type ):
		if type == csdefine.PET_TRAIN_TYPE_COMMON:
			self.pyBtnTrain_.enable = False
			self.pyBtnAsTrain_.enable = True
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "comUpgrade" )
		elif type == csdefine.PET_TRAIN_TYPE_HARD:
			self.pyBtnTrain_.enable = True
			self.pyBtnAsTrain_.enable = False
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "hardUpgrade" )
		else:
			self.pyBtnTrain_.enable = True
			self.pyBtnAsTrain_.enable = True
			self.pyCurState_.text = labelGather.getText( "PlayerProperty:GemPanel", "notUpgrade" )

	def __onTrainTimeChange( self, secnd ):# ʣ�����ʱ��
#		timeStr = formulas.secondToStrTime( secnd )
		hours = secnd / 3600
		minutes = ( secnd % 3600 )/60
		self.pyStRemainTime_.text = labelGather.getText( "PlayerProperty:GemPanel", "remainTime" )%( hours, minutes )

#	def __onTrainPointChange( self, point ):
#		pass
#		self.__pyStPoint.text = str( point ) + "��"

	def __onExpChange( self, exp ): # ��ʯ����ı�
		self.pyStCurExp_.text = labelGather.getText( "PlayerProperty:GemPanel", "expPoint" )%int( exp )

	def __onPetTrain( self ): #
		trainGem = BigWorld.player().ptn_getTrainGem()
		trainGem.startTrain( csdefine.PET_TRAIN_TYPE_COMMON )

	def __onPetAsTrain( self ): #�̿����
		trainGem = BigWorld.player().ptn_getTrainGem()
		trainGem.startTrain( csdefine.PET_TRAIN_TYPE_HARD )

	def __onPetPauseTrain( self ): #��ֹ����
		trainGem = BigWorld.player().ptn_getTrainGem()
		trainGem.stopTrain()

	def __onPetCharge( self ): #��ֵ
		player = BigWorld.player()
		trainGem = player.ptn_getTrainGem()
		time = int( self.pyChargeBox_.text )
		gold = int( self.pyStUnit_.text )*time
		trainGem.charge( gold )
		self.pyChargeBox_.text = ""

	def reset( self ):
		trainGem = BigWorld.player().ptn_getTrainGem()
		trainGem.stopCycleFlush()
		GemManage.reset( self )
