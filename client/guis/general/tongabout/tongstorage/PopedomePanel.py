# -*- coding: gb18030 -*-
#
# $Id: TongStorage.py, fangpengjun Exp $

"""
implement popedome panel

"""
from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.common.PyGUI import PyGUI
from guis.controls.ODComboBox import ODComboBox
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.SelectableButton import SelectableButton
from LabelGather import labelGather
import event.EventCenter as ECenter
import ItemTypeEnum
import csdefine

TONG_DUTY_ROWS = 8 #ÿҳ��ʾ8�����ְ��

class PopedomePanel( TabPanel ):

	def __init__( self, popePanel, pyBinder = None ):
		TabPanel.__init__( self, popePanel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		#self.pyBinder = pyBinder
		self.__upTag = {}
		self.__downTag = {}

		self.__pyDownLtCB = ODComboBox( popePanel.downLtCB )
		self.__pyDownLtCB.autoSelect = False
		self.__pyDownLtCB.enable = False
		self.__resetDownLtCB()

		self.__pyUpLtCB = ODComboBox( popePanel.upLtCB )
		self.__pyUpLtCB.autoSelect = False
		self.__pyUpLtCB.enable = False
		self.__resetUpLtCB()

		self.__pyDutiesPanel = DutiesPanel( popePanel.dutiesPanel )

		selectTitle = popePanel.selectPanel.bgTitle.stTitle		# ѡ�����
		setOutTitle = popePanel.setOutPanel.bgTitle.stTitle		# ȡ������
		setInTitle = popePanel.setInPanel.bgTitle.stTitle		# ��������

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( selectTitle, "StorageWindow:popedomePanel", "rbSLTitle" )				# ѡ�����
		labelGather.setLabel( setOutTitle, "StorageWindow:popedomePanel", "rbSOTitle" )				# ȡ������
		labelGather.setLabel( setInTitle, "StorageWindow:popedomePanel", "rbSITitle" )				# ��������
		labelGather.setLabel( popePanel.stDownLt, "StorageWindow:popedomePanel", "rbDownLt" )		# ��������Ʒ��
		labelGather.setLabel( popePanel.stUpLt, "StorageWindow:popedomePanel", "rbUpLt" )			# ��������Ʒ��

		self.__initBagBtns( popePanel.bagsPanel )

	def __initBagBtns( self, bagsPanel ):
		self.__pyBagBtns = SelectorGroup()
		for name, item in bagsPanel.children:
			if name.startswith( "bagBtn_" ):
				index = int( name.split( "_" )[1] )
				pyBagBtn = SelectableButton( item )
				pyBagBtn.setStatesMapping( UIState.MODE_R3C1 )
				pyBagBtn.index = index
				pyBagBtn.text = ""
				pyBagBtn.visible = False
				pyBagBtn.commonForeColor = 1, 255, 216, 127
				self.__pyBagBtns.addSelector( pyBagBtn )
		self.__pyBagBtns.onSelectChanged.bind( self.__onBagSelected )

	def __resetDownLtCB( self ):
		for key, keyStr in self.pyBinder._quality_map.iteritems(): #��ʼ��Ʒ��������
			keyStr = labelGather.getText( "StorageWindow:main", "miColor", keyStr )
			self.__pyDownLtCB.addItem( keyStr )
			self.__downTag[keyStr] = key
		self.__pyDownLtCB.onItemLClick.bind( self.__onSetDownLt )

	def __resetUpLtCB( self ):
		for key, keyStr in self.pyBinder._quality_map.iteritems(): #��ʼ��Ʒ��������
			keyStr = labelGather.getText( "StorageWindow:main", "miColor", keyStr )
			self.__pyUpLtCB.addItem( keyStr )
			self.__upTag[keyStr] = key
		self.__pyUpLtCB.onItemLClick.bind( self.__onSetUpLt )
	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		pass
#		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onUpdateLevel			# level changed trigger

		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	# --------------------------------------------------------
	def __onBagSelected( self, pyBag ): #ѡ��ĳ���ֿ�
		player = BigWorld.player()
		self.__pyDownLtCB.enable = pyBag is not None
		self.__pyUpLtCB.enable = pyBag is not None
		index = pyBag.index
		storagePopedoms = player.storageBagPopedom
		for storagePopedom in storagePopedoms:
			if storagePopedom["bagID"] == index:
				qualityUpLt = storagePopedom["qualityUpLimit"]
				qualityDownLt = storagePopedom["qualityLowerLimit"]
				fetchLimits = storagePopedom["fetchItemLimit"]
				self.__setDownLtCBIndex( qualityDownLt, qualityUpLt )
#				self.__pyDownLtCB.selIndex = qualityDownLt -1
				self.__setUpLtCBIndex( qualityDownLt, qualityUpLt )
				self.__pyDutiesPanel.setDutiesPope( index, fetchLimits ) #��ʼ�����ְ���ȡ����
				break

	def __setDownLtCBIndex( self, downQuality, upQuality ): #����������������
		self.__pyDownLtCB.clearItems()
		self.__pyDownLtCB.onItemLClick.unbind( self.__onSetDownLt )
		qualitis = []
		selIndex = 0
		for key, keyStr in self.pyBinder._quality_map.iteritems():
			if key > upQuality:continue
			keyStr = labelGather.getText( "StorageWindow:main", "miColor", keyStr )
			qualitis.append( key )
			self.__downTag[keyStr] = key
			self.__pyDownLtCB.addItem( keyStr )
		qualitis.sort()
		if downQuality in qualitis:
			selIndex = qualitis.index( downQuality )
		self.__pyDownLtCB.selIndex = selIndex
		self.__pyDownLtCB.onItemLClick.bind( self.__onSetDownLt )

	def __setUpLtCBIndex( self, downQuality, upQuality ):
		self.__pyUpLtCB.clearItems()
		self.__pyUpLtCB.onItemLClick.unbind( self.__onSetUpLt )
		qualitis = []
		selIndex = 0
		for key, keyStr in self.pyBinder._quality_map.iteritems():
			if key < downQuality:continue
			keyStr = labelGather.getText( "StorageWindow:main", "miColor", keyStr )
			qualitis.append( key )
			self.__upTag[keyStr] = key
			self.__pyUpLtCB.addItem( keyStr )
		qualitis.sort()							# �����Ǵ�С����
		if upQuality in qualitis:
			selIndex = qualitis.index( upQuality )
		self.__pyUpLtCB.selIndex = selIndex
		self.__pyUpLtCB.onItemLClick.bind( self.__onSetUpLt )

	def __onSetDownLt( self, pyLtItem ): #���ô�ȡ��ƷƷ������
		downItem = self.__pyDownLtCB.selItem
		downQuality = self.__downTag[downItem]
		selPyBtn = self.__pyBagBtns.pyCurrSelector
		selIndex = self.__pyBagBtns.pySelectors.index( selPyBtn )
		BigWorld.player().tong_changeStorageQualityLower( selIndex, downQuality )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_DOWN_QUALITY", selIndex, downQuality )
		upItem = self.__pyUpLtCB.selItem #��ǰѡ�������
		upQuality = self.__upTag[upItem]
		self.__setUpLtCBIndex( downQuality, upQuality )

	def __onSetUpLt( self, pyLtItem ): #���ô�ȡ��ƷƷ������
		upItem = self.__pyUpLtCB.selItem
		upQuality = self.__upTag[upItem]
		selPyBtn = self.__pyBagBtns.pyCurrSelector
		selIndex = self.__pyBagBtns.pySelectors.index( selPyBtn )
		BigWorld.player().tong_changeStorageQualityUp( selIndex, upQuality )
		ECenter.fireEvent( "EVT_ON_TOGGLE_TONG_UP_QUALITY", selIndex, upQuality )
		downItem = self.__pyDownLtCB.selItem
		downQuality = self.__downTag[downItem]
		self.__setDownLtCBIndex( downQuality, upQuality )

	#----------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def resetPanel( self ):
		player = BigWorld.player()
		storagePopedom = player.storageBagPopedom
		for popedom in storagePopedom: #���òֿ�ѡ��ť״̬
			bagID = popedom["bagID"]
			bagName = popedom["bagName"]
			pyBagBtn = self.__pyBagBtns.pySelectors[bagID]
			if bagName == "":
				pyBagBtn.text = self.pyBinder._nums_map[bagID]
			else:
				pyBagBtn.text = bagName
			pyBagBtn.visible = True
			pyBagBtn.commonForeColor = 1, 255, 216, 255
		self.__pyDutiesPanel.setDutySetersInfo( 0 )
		selBagBtn = self.__pyBagBtns.pySelectors[0]
		selBagBtn.selected = True
		selBagBtn.setState( UIState.PRESSED )
		self.__onBagSelected( selBagBtn )

	def onLeaveWorld( self ) :

		pass

# -----------------------------------------------------------------------
# ���ְ�����
# -----------------------------------------------------------------------
import Const

class DutiesPanel( PyGUI ) :

	_cc_amount = 8

	def __init__( self, panel ) :
		PyGUI.__init__( self, panel )
		self.__initDuties( panel )

	def __initDuties( self, panel ):
		self.__pyDutySeters = {}
		for name, item in panel.children:
			if name.startswith( "dutyseter_" ):
				index = int( name.split( "_" )[1] )
				if index > 3:
					pyDutySeter = DutySeter( item )
					self.__pyDutySeters[index] = pyDutySeter
				else:  #�����޸İ��֮������ֻ���ĸ�ְλ����Ӧ��ȥ��������ʾ
					pyDutySeter = DutySeter( item )
					self.__pyDutySeters[index] = pyDutySeter
					self.__pyDutySeters[index].visible = False
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def setDutiesPope( self, bagIndex, fetchLimits ):
		for index, pyDutySeter in self.__pyDutySeters.iteritems():
			gradeIndex = index - 3
			pyDutySeter.bagID = bagIndex
			if fetchLimits.has_key( gradeIndex ):
				fetchNum = fetchLimits[gradeIndex]
				pyDutySeter.setFetchNum( gradeIndex, fetchNum )

	def setDutySetersInfo( self, bagIndex ): #��ʼ�����ְ���ȡ��Ϣ
		tong_dutyNames = BigWorld.player().tong_dutyNames
		for index, pyDutySeter in self.__pyDutySeters.iteritems():
			dutyGrade = index - 3
			pyDutySeter.dutyGrade = dutyGrade
			pyDutySeter.bagID = bagIndex
			if tong_dutyNames.has_key( dutyGrade ):
				custName = tong_dutyNames[dutyGrade]
				pyDutySeter.setCustomName( custName )
				pyDutySeter.setStandardName( Const.TONG_GRADE_MAPPING[dutyGrade] )

# --------------------------------------------------------------------------
# ���ְ��ؼ�
# --------------------------------------------------------------------------
from guis.controls.RadioButton import RadioButton
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.Control import Control

class DutySeter( Control ):

	__cg_memberset = None
	__cg_flashCBID = 0
	__cg_fetch_Nums = [1, 2, 3, 4, 5, 10, 15, 20, 30000]

	def __init__( self, dutyseter):
		Control.__init__( self, dutyseter )
		self.__fetchNum = {}
		self.__pyStName = StaticText( dutyseter.memberName ) #��Ա����
		self.__pyStName.text = ""

		self.__pyStDuty = StaticText( dutyseter.memberDuty ) #��Աְ��
		self.__pyStDuty.text = ""

		self.__pyRBDisable = RadioButton( dutyseter.radioDisable ) #���ɴ�ȡ��ѡ��ť
#		self.__pyRBDisable.onLClick.bind( self.__setDisableFetch )
		self.__pyRBDisable.canAcced = False

		self.__pyRBEnable = RadioButton( dutyseter.radioEnable ) #�ɴ�ȡ��ѡ��ť
#		self.__pyRBDisable.onLClick.bind( self.__setEnableFetch )
		self.__pyRBEnable.canAcced = True

		self.__rbArray = CheckerGroup()
		self.__rbArray.addCheckers( self.__pyRBDisable, self.__pyRBEnable )
		self.__rbArray.onCheckChanged.bind( self.__onEnableChanged )

		self.__pyAmountCB = ODComboBox( dutyseter.amountCB )
		self.__pyAmountCB.autoSelected = False

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( dutyseter.enableText, "StorageWindow:popedomePanel", "rbEnable" )		# ��ȡ��
		labelGather.setLabel( dutyseter.disableText, "StorageWindow:popedomePanel", "rbDisable" )	# ����ȡ��
		labelGather.setLabel( dutyseter.takeNumText, "StorageWindow:popedomePanel", "rbTakeNum" )	# ÿ�տ�ȡ

		for index, fetchNum in enumerate( self.__cg_fetch_Nums ):
			if fetchNum == 30000:
				cbItemText = labelGather.getText( "StorageWindow:popedomePanel", "miInfinity" )
			else:
				cbItemText = labelGather.getText( "StorageWindow:popedomePanel", "miFetchNum", fetchNum )
			#pyCBItem.h_anchor = "CENTER"
			self.__fetchNum[index] = fetchNum
			self.__pyAmountCB.addItem( cbItemText )
		self.__pyAmountCB.onItemLClick.bind( self.__onSetFetchNum )

		self.__flasher = dutyseter.flasher
		self.__flasher.speed = 0.3

		self.__bagID = 0 #�ֿ�ID
		self.__dutyGrade = 0 #ְ��

	def __onEnableChanged( self, pyRadio ):
		if pyRadio is None:return
		canAcced = pyRadio.canAcced
		self.__pyAmountCB.enable = canAcced
		fetchNum = 0
		if canAcced:
			selIndex = self.__pyAmountCB.selIndex
			fetchNum = self.__fetchNum[selIndex]
		BigWorld.player().tong_changeStorageBagLimit( self.__bagID, self.__dutyGrade, fetchNum )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onSetFetchNum( self, pyCBItem ):
		selIndex = self.__pyAmountCB.selIndex
		fetchNum = self.__fetchNum[selIndex]
		BigWorld.player().tong_changeStorageBagLimit( self.__bagID, self.__dutyGrade, fetchNum )

	def __flash( self ) :
		"""
		��˸����Ŀ�ݼ�������
		"""
		value = self.__flasher.value
		if value > 0.99 :
			self.__flasher.value = 0.5
		elif value < 0.51 :
			self.__flasher.value = 1.0
		BigWorld.cancelCallback( self.__cg_flashCBID )
		self.__cg_flashCBID = BigWorld.callback( 0.6, self.__flash )

	def __unflash( self ) :
		"""
		ֹͣ��˸
		"""
		BigWorld.cancelCallback( self.__cg_flashCBID )
		self.__flasher.value = 1.0
		self.__flasher.reset()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		���̰�������ʱ������
		"""
		Control.onKeyDown_( self, key, mods )
		self.__flash()
		return True

	def onKeyUp_( self, key, mods ):
		Control.onKeyUp_( self, key, mods )
		self.__unflash()
		return True

	# -------------------------------------------------
	def onTabIn_( self ) :
		"""
		����ý���ʱ������
		"""
		Control.onTabIn_( self )
		self.__flash()

	def onTabOut_( self ) :
		"""
		�������뿪ʱ������
		"""
		Control.onTabOut_( self )
		self.__unflash()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setFetchNum( self, tongGrade, fetchNum ): #����ÿ�տ�ȡ��Ʒ����
		if tongGrade == csdefine.TONG_DUTY_CHIEF: #����
			self.__pyRBEnable.checked = True
			self.__pyRBEnable.enable = False
			self.__pyRBDisable.enable = False
			self.__pyAmountCB.selIndex = -1
			self.__pyAmountCB.enable = False
		else: #����ְ��
			selIndex = 0
			self.__pyRBEnable.checker_.visible = fetchNum > 0
			self.__pyRBDisable.checker_.visible = fetchNum <= 0
			self.__pyAmountCB.enable = fetchNum > 0
			if fetchNum > 0:
				if fetchNum in self.__cg_fetch_Nums:
					selIndex = self.__cg_fetch_Nums.index( fetchNum )
			self.__pyAmountCB.selIndex = selIndex

	def setCustomName( self, custName ): #�����Զ���ְ������
		self.__pyStName.text = custName

	def setStandardName( self, standardName ): #���ñ�׼ְ������
		self.__pyStDuty.text = standardName

	def _getBagID( self ):
		return self.__bagID

	def _setBagID( self, bagID ):
		self.__bagID = bagID

	def _getDutyGrade( self ):
		return self.__dutyGrade

	def _setDutyGrade( self, dutyGrade ):
		self.__dutyGrade = dutyGrade

	bagID = property( _getBagID, _setBagID )
	dutyGrade = property( _getDutyGrade, _setDutyGrade )
