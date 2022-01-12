# -*- coding: gb18030 -*-
#
# $Id: TongStorage.py, fangpengjun Exp $

"""
implement tongbank window class

"""
from guis import *
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from GoodsPanel import GoodsPanel
from PopedomePanel import PopedomePanel
from LogsPanel import LogsPanel
from LabelGather import labelGather
from gbref import rds
import ItemTypeEnum
import GUIFacade
import csdefine
import csconst
import time

STORAGEBAG_MAX_ORDER = 80

class StorageWindow( Window ):

	_nums_map = { csdefine.TONG_STORAGE_ONE: labelGather.getText( "StorageWindow:main", "miStorageOne" ),
			csdefine.TONG_STORAGE_TWO: labelGather.getText( "StorageWindow:main", "miStorageTwo" ),
			csdefine.TONG_STORAGE_THREE: labelGather.getText( "StorageWindow:main", "miStorageThree" ),
			csdefine.TONG_STORAGE_FOUR: labelGather.getText( "StorageWindow:main", "miStorageFour" ),
			csdefine.TONG_STORAGE_FIVE: labelGather.getText( "StorageWindow:main", "miStorageFive" ),
			csdefine.TONG_STORAGE_SIX: labelGather.getText( "StorageWindow:main", "miStorageSix" )
			}

	_quality_map = { ItemTypeEnum.CQT_WHITE: labelGather.getText( "StorageWindow:main", "miWhite" ),
			ItemTypeEnum.CQT_BLUE: labelGather.getText( "StorageWindow:main", "miBlue" ),
			ItemTypeEnum.CQT_GOLD: labelGather.getText( "StorageWindow:main", "miGold" ),
			ItemTypeEnum.CQT_PINK: labelGather.getText( "StorageWindow:main", "miPink" ),
			ItemTypeEnum.CQT_GREEN: labelGather.getText( "StorageWindow:main", "miGreen" )
			}

	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongbank/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		self.__bagsFetchNum = {} #��¼ÿ���ֿ��ȡ����Ʒ����
		self.__qualities = {} #������ʱ��¼Ʒ�ʸı�
		self.__trapID = None

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# ��ӵ�MutexGroup.TRADE1������

	def __initialize( self, wnd ):
		self.__pyStLimNum = StaticText( wnd.stLimNum )
		self.__pyStLimNum.text = ""
		self.__pyStQuality = StaticText( wnd.stQuality )
		self.__pyStQuality.text = ""
		self.__pyTabCtr = TabCtrl( wnd.tabCtrl )
		self.__pyGoodspanel = GoodsPanel( wnd.tabCtrl.panel_0, self ) #�����Ʒ���
		self.__pyPopedomePanel = PopedomePanel( wnd.tabCtrl.panel_6, self ) #��ȡȨ�����
		self.__pyLogsPanel = LogsPanel( wnd.tabCtrl.panel_7 ) #��ȡ��־���
		pages = {}
		pyBtns = {}
		for name, item in wnd.tabCtrl.children:
			if name.startswith( "btn_" ):
				index = int( name.split( "_" )[1] )
				pyBankBtn = TabButton( item )
				pyBankBtn.setStatesMapping( UIState.MODE_R4C1 )
				pyBankBtn.visible = True
				if self._nums_map.has_key( index ):
					pyBankBtn.enable = False
					pyBankBtn.text = self._nums_map[index]
					pyPage = TabPage( pyBankBtn, self.__pyGoodspanel )
					pages[index] = pyPage
				else:
					pyBtns[index] = pyBankBtn
		pyPage6 = TabPage( pyBtns[6], self.__pyPopedomePanel )
		pyPage7 = TabPage( pyBtns[7], self.__pyLogsPanel )
		self.__pyTabCtr.addPages( pages[0], pages[1], pages[2], pages[3], pages[4], pages[5], pyPage6, pyPage7 )
		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onTabSelectChanged )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( pyBtns[6], "StorageWindow:main", "btnGrade" )			# Ȩ������
		labelGather.setPyBgLabel( pyBtns[7], "StorageWindow:main", "btnItemMsg" )		# ��Ʒ��Ϣ
		labelGather.setLabel( wnd.lbTitle, "StorageWindow:main", "rbTitle" )			# ���ֿ�

	# -------------------------------------------------------
	# pravite
	# -------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_TONG_ENTER_STORAGE"] = self.__onTongStorageEnter #�򿪰��ֿ����
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_NAME_CHANGE"] = self.__onBagNameChange	#�ֿ����Ƹı�֪ͨ
		self.__triggers["EVT_ON_TOGGLE_TONG_ACTIVATE_BANK_SUCCESS"] 	= self.__onActivateBag	#��������ɹ�
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_FETCH_CHANGE"] = self.__onStorageFetch #��ȡ�����ı�
		self.__triggers["EVT_ON_TOGGLE_TONG_DOWN_QUALITY"] = self.__onDownQualityChange #��Ʒ��ȡƷ�����޸ı�
		self.__triggers["EVT_ON_TOGGLE_TONG_UP_QUALITY"] = self.__onUpQualityChange #��Ʒ��ȡƷ�����޸ı�
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------------
	def __onTongStorageEnter( self ):
		targeter= GUIFacade.getGossipTarget()
		if targeter is None:
			targeter= BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr(targeter, "getRoleAndNpcSpeakDistance" ):
			distance = targeter.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot( targeter.matrix,distance, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		self.show()

	def __delTrap( self ) :
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )									#ɾ����ҵĶԻ�����
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:
			self.__delTrap()
			self.hide()														#���ص�ǰ���״���
	# ---------------------------------------------------------------
	def __onBagNameChange( self, bagID, name ):
		pyBankBtn = self.__pyTabCtr.pyPages[bagID].pyBtn
		if name == "":
			pyBankBtn.text = self._nums_map[bagID]
		else:
			pyBankBtn.text = name

	def __onActivateBag( self, index ):
		pyPage = self.__pyTabCtr.pyPages[index]
		pyPage.enable = True

	def __onTabSelectChanged( self, pyCtrl ):
		pySelPage = pyCtrl.pySelPage
		bagIndex = pySelPage.index
		self.__pyTabCtr.pyPages[bagIndex].selected = True
		player = BigWorld.player()
		self.__pyGoodspanel.visible = bagIndex in self._nums_map
		self.__pyPopedomePanel.visible = bagIndex == 6
		self.__pyLogsPanel.visible = bagIndex == 7
		if bagIndex in self._nums_map: #�����Ϊ�ֿⱳ��
			self.__pyGoodspanel.setItems( bagIndex )
		bagPopedoms = player.storageBagPopedom
		tongGrade = player.tong_grade
		fetchNumber = 0
		ltLowerQuality = ""
		ltUpQuality = ""
		self.__pyStLimNum.text = ""
		for bagPopedom in bagPopedoms: #��ȡ����ڸð����ɴ�ȡ��Ʒ��������ƷƷ������
			if bagPopedom["bagID"] != bagIndex:continue
			bagID = bagPopedom["bagID"]
			downQuality = self.__qualities[bagID]["downQuality"]
			upQuality = self.__qualities[bagID]["upQuality"]
			ltLowerQuality = labelGather.getText( "StorageWindow:main", "miColor", self._quality_map[downQuality] )
			ltUpQuality = labelGather.getText( "StorageWindow:main", "mi_Color", self._quality_map[upQuality] )
		if self.__bagsFetchNum.has_key( bagIndex ) and bagIndex in self._nums_map:
			remainNum = self.__bagsFetchNum[bagIndex]
			if remainNum < 0: remainNum = 0
			self.__pyStLimNum.text = labelGather.getText( "StorageWindow:main", "miCanTakeItem", remainNum )
		self.__pyStQuality.text = ltLowerQuality + ltUpQuality

	def __onStorageFetch( self, amount ):
		selIndex = self.__pyTabCtr.pySelPage.index
		remainNum = 0
		if self.__bagsFetchNum.has_key( selIndex ):
			remainNum = self.__bagsFetchNum[selIndex] - amount
			self.__bagsFetchNum[selIndex] = remainNum
		if remainNum < 0: remainNum = 0
		self.__pyStLimNum.text = labelGather.getText( "StorageWindow:main", "miCanTakeItem", remainNum )

	def __onDownQualityChange( self, bagIndex, downQuality ):
		if self.__qualities[bagIndex]["downQuality"] != downQuality:
			self.__qualities[bagIndex]["downQuality"] = downQuality
		selIndex = self.__pyTabCtr.pySelPage
		if selIndex == bagIndex:
			upQuality = self.__qualities[bagIndex]["upQuality"]
			ltLowerQuality = labelGather.getText( "StorageWindow:main", "miColor", self._quality_map[downQuality] )
			ltUpQuality = labelGather.getText( "StorageWindow:main", "mi_Color", self._quality_map[upQuality] )
			self.__pyStLimNum.text = ltLowerQuality + ltUpQuality

	def __onUpQualityChange( self, bagIndex, upQuality ):
		if self.__qualities[bagIndex]["upQuality"] != upQuality:
			self.__qualities[bagIndex]["upQuality"] = upQuality
		selIndex = self.__pyTabCtr.pySelPage
		if selIndex == bagIndex:
			downQuality = self.__qualities[bagIndex]["downQuality"]
			ltLowerQuality = labelGather.getText( "StorageWindow:main", "miColor", self._quality_map[downQuality] )
			ltUpQuality = labelGather.getText( "StorageWindow:main", "mi_Color", self._quality_map[upQuality] )
			self.__pyStLimNum.text = ltLowerQuality + ltUpQuality

	def __setBankBtnState( self ):
		"""
		��ʼ����ť״̬
		"""
		player = BigWorld.player()
		player.onTongStorage( True )
		bagPopedoms = player.storageBagPopedom
		tongGrade = player.tong_grade
		bagIDs = []
		for bagPopedom in bagPopedoms:
			bagID = bagPopedom["bagID"]
			bagName = bagPopedom["bagName"]
			bagPage = self.__pyTabCtr.pyPages[bagID]
			try:
				haveFetchNum = player.fetchRecord[bagID]
			except KeyError:
				haveFetchNum = 0
			fetchNums = bagPopedom["fetchItemLimit"]
			fetchNumber = fetchNums[tongGrade] - haveFetchNum
			downQuality = bagPopedom["qualityLowerLimit"]
			upQuality = bagPopedom["qualityUpLimit"]
			dict = { "downQuality" :downQuality,
				"upQuality":upQuality
				}
			self.__qualities[bagID ] = dict
			# �桢ȡȨ�޺ϲ�
			canShow = player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHET_STORAGE_ITEM_ACCESS )
			bagPage.enable = canShow
			if canShow: #�����ȡ��������0����ɵ���ð�ť
				bagIDs.append( bagID )
			else:
				bagPage.enable = False
			self.__bagsFetchNum[bagID] = fetchNumber
			if bagName == "":
				bagPage.pyBtn.text = self._nums_map[bagID]
			else:
				bagPage.pyBtn.text = bagName
		pySelIndex = 0
		if len( bagIDs ) > 0: #Ĭ�ϵ�һ���ɴ�ȡ�ֿ�Ϊѡ��ֿ�
			pySelIndex = bagIDs[0]
		else: #û�пɴ�ȡ�ֿ⣬ֻ�ܿ���ȡ��־
			pySelIndex = -1
			self.__pyGoodspanel.freezeItems()
		pySelPage = self.__pyTabCtr.pyPages[pySelIndex]
		pySelPage.selected = True
		self.__onTabSelectChanged( pySelPage.pyTabCtrl )
	#----------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def getCurStorageIndex( self ):
		return  self.__pyTabCtr.pySelPage.index

	def show( self ):
		self.__setBankBtnState() #��ʼ����ť״̬

		# �������
		self.__pyTabCtr.pyPages[-2].pyBtn.enable = BigWorld.player().tong_grade == csdefine.TONG_DUTY_CHIEF #ֻ�а����������ô�ȡȨ��
		Window.show( self )
		self.__pyPopedomePanel.resetPanel()

	def hide( self ):
		self.__pyLogsPanel.clear()
		BigWorld.player().onTongStorage( False )
		for pyPage in self.__pyTabCtr.pyPages:
			if pyPage.index in self._nums_map:
				pyPage.enable = False
		self.__pyGoodspanel.onLeaveWorld()
		self.__qualities = {}
		Window.hide( self )

	def onLeaveWorld( self ) :
		self.__pyStLimNum.text = ""
		self.__pyStQuality.text = ""
		self.__bagsFetchNum = {}
		self.__pyGoodspanel.onLeaveWorld()
		self.__pyPopedomePanel.onLeaveWorld()
		self.__pyLogsPanel.onLeaveWorld()
		self.hide()
