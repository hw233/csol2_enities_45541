# -*- coding: gb18030 -*-
#
# $Id: LogsPanel.py, fangpengjun Exp $

"""
implement logs panel

"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from LabelGather import labelGather
import GUIFacade
import csdefine

class LogsPanel( TabPanel ):
	def __init__( self, logsPanel ):
		TabPanel.__init__( self, logsPanel )
		self.__initTabCtrl( logsPanel )
		self.__triggers = {}
		self.__registerTriggers()

	def __initTabCtrl( self, panel ):
		self.__pyTabCtrl = TabCtrl( panel )
		self.__pySaveTabBtn = TabButton( panel.btn_0 ) #������־
		self.__pySaveLogs = LogPanel( panel.panel_0 )
		self.__pyTabCtrl.addPage( TabPage( self.__pySaveTabBtn, self.__pySaveLogs ) )

		self.__pyTakeBtn = TabButton( panel.btn_1 ) #ȡ����־
		self.__pyTakeLogs = LogPanel( panel.panel_1 )
		self.__pyTabCtrl.addPage( TabPage( self.__pyTakeBtn, self.__pyTakeLogs ) )

		self.__pyColligateBtn = TabButton( panel.btn_2 ) #��ȡ�ۺ���־
		self.__pyColligateLogs = LogPanel( panel.panel_2 )
		self.__pyTabCtrl.addPage( TabPage( self.__pyColligateBtn, self.__pyColligateLogs ) )

		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onLogsPanelChange )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pySaveTabBtn, "StorageWindow:logsPanel", "btnSave" )			# ����
		labelGather.setPyBgLabel( self.__pyTakeBtn, "StorageWindow:logsPanel", "btnTake" )				# ȡ��
		labelGather.setPyBgLabel( self.__pyColligateBtn, "StorageWindow:logsPanel", "btnColligate" )	# �ۺ�

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register all events
		"""
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_LOG"] = self.__onTongStorageLog #�ֿ������־
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )
	# --------------------------------------------------------------
	def __onTongStorageLog( self, log ):
		operate = log[1] #��ȡ����
		if operate == csdefine.TONG_STORAGE_OPERATION_ADD:#������Ʒlog
			self.__pySaveLogs.addLog( log )
		else:
			self.__pyTakeLogs.addLog( log ) #ȡ��logs
		self.__pyColligateLogs.addLog( log ) #�ۺ�logs

	def __onLogsPanelChange( self, pyPage ):
		player = BigWorld.player()
		storageLogs = player.tong_storageLog

	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def clear( self ):
		self.__pySaveLogs.clearLogs()
		self.__pyTakeLogs.clearLogs()
		self.__pyColligateLogs.clearLogs()

	def onLeaveWorld( self ):
		self.clear()
# ---------------------------------------------------------------------
# ��־���
# ---------------------------------------------------------------------
from guis.controls.TabCtrl import TabPanel
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
import items
import time
itemsInstance = items.instance()

class LogPanel( TabPanel ):
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__pyLogsList = ItemsPanel( tabPanel.listPanel, tabPanel.scrollBar )

	def addLog( self, log ):
		memberName, operate, itemID, itemAmount, bagID, accTime = log
		player = BigWorld.player()
		storagePopedoms = player.storageBagPopedom
		bagName = ""
		for storagePopedom in storagePopedoms:
			if storagePopedom["bagID"] == bagID:
				bagName = storagePopedom["bagName"]
		if bagName == "":
			bagName = labelGather.getText( "StorageWindow:logsPanel", "miStorage", bagID+1 )
		item = player.createDynamicItem( itemID )
		itemName = item.name()
		qtColor = item.getQualityColor()
		logRT = CSRichText()
		logRT.maxWidth = 550.0
		timeTupe = time.localtime( accTime )
		timeStr = labelGather.getText( "StorageWindow:logsPanel", "miTime", timeTupe[0], timeTupe[1], timeTupe[2], timeTupe[3], timeTupe[4] )
		timeStr = PL_Font.getSource( timeStr, fc = ( 255, 255, 255 ) )
		memberName = PL_Font.getSource( memberName, fc = ( 255, 255, 0 ) )
		itemCount = PL_Font.getSource( str( itemAmount ), fc = ( 255, 0, 0 ) )
		itemName = PL_Font.getSource( itemName, fc = qtColor )
		if operate == csdefine.TONG_STORAGE_OPERATION_ADD: #����
			logRT.text = labelGather.getText( "StorageWindow:logsPanel", "miLogIn", timeStr, memberName, bagName, itemCount, itemName )
		else:
			logRT.text = labelGather.getText( "StorageWindow:logsPanel", "miLogOut", timeStr, memberName, bagName, itemCount, itemName )
		self.__pyLogsList.addItem( logRT )

	def clearLogs( self ):
		self.__pyLogsList.clearItems()
