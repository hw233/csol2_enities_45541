# -*- coding: gb18030 -*-
#
# $Id: HelpWindow.py,v 1.1 2008-04-14 10:26:35 huangyongwei Exp $

"""
implement system helper class.

2008.04.10: writen by huangyongwei
"""

from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from config.client.help.ShowOutputLevels import ShowLevelDatas
from config.client.help.PlayPointHelpConfig import Datas as pointDatas
from guis.general.npctalk.LevelUpAwardReminder import LevelUpAwardReminder
from Notifier import KeyNotifier, LevelNotifier
from Prompter import Prompter
from Guider import Guider
from Searcher import Searcher
from LevelHelper import LevelHelper
from OutputHelper import OutputHelper
from PlayPointHelper import PlayPointHelper
from LabelGather import labelGather

class HelpWindow( Window ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/helper/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		helper_maps = { 0: Prompter, 1: Guider, 2: Searcher, 3: LevelHelper, 4: OutputHelper, 5: PlayPointHelper }
		self.__pyTabCtrl = TabCtrl( wnd.tc )									# ��ҳѡ�
		index = 0
		while True :											#��ʼ��TabCtrl
			tabName = "btn_" + str( index )
			tab = getattr( wnd.tc, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			panel = getattr( wnd.tc, panelName, None )
			if panel is None : break
			pyBtn = TabButton( tab )
			pyBtn.setStatesMapping( UIState.MODE_R3C1 )
			labelGather.setPyBgLabel( pyBtn, "HelpWindow:main", "btn_%d"%index )
			scriptPanel = helper_maps.get( index, None )
			if scriptPanel is None:break
			pyPanel = scriptPanel( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTabCtrl.addPage( pyPage )
			index += 1
		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onTabSelectChanged )
		labelGather.setPyLabel( self.pyLbTitle_, "HelpWindow:main", "lbTitle" )

	# ---------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_HELP_WINDOW"] = self.__toggleGuider		# ��ʾ/���ذ�������
		self.__triggers["EVT_ON_HELP_SEARCH"] = self.__onSearchHelp				# ��������ָ��
		self.__triggers["EVT_ON_SHOW_COURSE_HELP"] = self.__onShowCourse		# ��ʾ������ʾ
		self.__triggers["EVT_ON_TOGGLE_UPGRADE_HELPER"] = self.__onUpgradeHelp	# �ȼ���ʾ
		self.__triggers["EVT_ON_GET_ITEMS_WINDOW_SHOW"] = self.__onOutputHelp	# ����������ʾ
		self.__triggers["EVT_ON_PHASES_TIPS_WINDOW_SHOW"] = self.__onPlayPoint	# ��������ʾ
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onRoleLevelChanged	# ��ɫ�ȼ��ı�ʱ������
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __onTabSelectChanged( self ) :
		"""
		���ݷ�ҳ���ô��ڱ���
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		index = pySelPage.index
		if index == 3:
			pySelPage.pyPanel.showLevelTips()
		elif index == 5:
			pySelPage.pyPanel.showPlayPoint()

	# -------------------------------------------------
	def __toggleGuider( self ) :
		"""
		��ʾ/���ذ�������
		"""
		if self.visible :
			self.hide()
		else :
			self.__pyTabCtrl.pyPages[1].selected = True
			self.show()

	def __onSearchHelp( self, text ) :
		"""
		��������ָ��
		"""
		pySeacher = self.__pyTabCtrl.pyPages[2]
		pySeacher.selected = True
		pySeacher.pyPanel.searchTopic( text )
		if not self.visible : self.show()

	def __onShowCourse( self ) :
		"""
		��ʾ���̰���
		"""
		pyPrompter = self.__pyTabCtrl.pyPages[0]
		pyPrompter.selected = True
		pyPrompter.pyPanel.showCourseHelp()
		if not self.visible : self.show()

	def __onUpgradeHelp( self ):
		"""
		��ɫ�ȼ��ı�ʱ������
		"""
		pyHelper = self.__pyTabCtrl.pyPages[3]
		pyHelper.selected = True
		pyHelper.pyPanel.showLevelTips()
		if not self.visible : self.show()
		else:self.hide()

	def __onOutputHelp( self ):
		"""
		����������ʾ����
		"""
		pyOutput = self.__pyTabCtrl.pyPages[4]
		pyOutput.selected = True
		pyOutput.pyPanel.showOutput()
		if not self.visible : self.show()
		else:self.hide()

	def __onPlayPoint( self ):
		"""
		������������ʾ
		"""
		pyPlayPoint = self.__pyTabCtrl.pyPages[5]
		pyPlayPoint.selected = True
		pyPlayPoint.pyPanel.showPlayPoint()
		if not self.visible : self.show()
		else:self.hide()

	def __onRoleLevelChanged( self, oldLevel, level ):
		"""
		��ɫ�ȼ��ı䴥���йذ�����ʾ
		"""
		LevelUpAwardReminder.instance().onRoleLevelChanged( oldLevel, level )
		if oldLevel != level :
			LevelNotifier.instance().show()
		# �߻�˵������ͬʱ����������ʾ��������ô��
		if level in ShowLevelDatas :
			KeyNotifier.showType = "u"
			KeyNotifier.instance().show()
		elif level in pointDatas : #���
			KeyNotifier.showType = "a"
			KeyNotifier.instance().show()
		else:
			KeyNotifier.getInstance() and KeyNotifier.getInstance().dispose()
		pySelPage = self.__pyTabCtrl.pySelPage
		helperPanel = pySelPage.pyPanel
		index = pySelPage.index
		if index in [3, 5] and self.visible:
			helperPanel.onLevelChange( oldLevel, level )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onKeyDown_( self, key, mods ) :
		"""
		"""
		keyEventHandler = getattr( self.__pyTabCtrl.pySelPage.pyPanel, "keyEventHandler", None )
		if callable( keyEventHandler ) :
			return keyEventHandler( key, mods )
		return Window.onKeyDown_( self, key, mods )

	def onEnterWorld( self ) :
		"""
		����������ʱ������
		"""
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPage.pyPanel.onEnterWorld()

	def onLeaveWorld( self ) :
		"""
		���뿪����ʱ������
		"""
		self.hide()
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPage.pyPanel.onLeaveWorld()
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def hide( self ) :
		"""
		���ش���
		"""
		Window.hide( self )
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onWindowHid()
