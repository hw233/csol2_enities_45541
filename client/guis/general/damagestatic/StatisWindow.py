# -*- coding: gb18030 -*-
# $Id: StatisWindow.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.ListPanel import ListPanel
from SendWindow import SendWindow
from AbstractTemplates import Singleton
from config.client.msgboxtexts import Datas as mbmsgs
from guis import rds

class StatisWindow( Singleton, Window ):
	
	__instance = None
	titles_dsp = {	0: labelGather.getText( "Damagestatic:main", "dsp_0" ),
					1: labelGather.getText( "Damagestatic:main", "dsp_1" ),
					2: labelGather.getText( "Damagestatic:main", "dsp_2" ),
				}
	
	def __init__( self ):
		assert StatisWindow.__instance is None,"StatisWindow instance has been created"
		StatisWindow.__instance = self
		wnd = GUI.load( "guis/general/damagestatis/staticwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "damageStatis" )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_DamageStatis :
			INFO_MSG( str( self ) )
	
	# --------------------------------------------------
	# pravite
	# --------------------------------------------------
	def __initialize( self, wnd ):
		self.__pyListPanel = ListPanel( wnd.statisPanel.clipPanel, wnd.statisPanel.sbar )
		labelGather.setLabel( wnd.btnDama.lbText, "Damagestatic:main", "damageText" )
		labelGather.setLabel( wnd.btnValue.lbText, "Damagestatic:main", "damageValue" )
		for name, item in wnd.children:
			if not name.startswith( "topDsp_" ):continue
			index = int( name.split( "_" )[1] )
			pyTitleDsp = Control( item )
			pyTitleDsp.enable = True
			pyTitleDsp.crossFocus = True
			pyTitleDsp.index = index
			pyTitleDsp.onMouseEnter.bind( self.__onShowTitleDsp )
			pyTitleDsp.onMouseLeave.bind( self.__onHideTitleDsp )
		
		self.__pyBtnStart = Button( wnd.btnStart )				#开始
		self.__pyBtnStart.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnStart.dsp = labelGather.getText( "Damagestatic:main", "start" )
		self.__pyBtnStart.onLClick.bind( self.__onStart )
		self.__pyBtnStart.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnStart.onMouseLeave.bind( self.__onBtnMouseLeave )
		self.__pyBtnStart.onLMouseDown.bind( self.__onBtnMouseLeave )
		
		self.__pyBtnStop = Button( wnd.btnStop )				#停止
		self.__pyBtnStop.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnStop.dsp = labelGather.getText( "Damagestatic:main", "stop" )
		self.__pyBtnStop.onLClick.bind( self.__onStop )
		self.__pyBtnStop.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnStop.onMouseLeave.bind( self.__onBtnMouseLeave )
		self.__pyBtnStop.onLMouseDown.bind( self.__onBtnMouseLeave )
		
		self.__pyBtnShut = Button( wnd.btnShut )				#关闭
		self.__pyBtnShut.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnShut.dsp = labelGather.getText( "Damagestatic:main", "close" )
		self.__pyBtnShut.onLClick.bind( self.__onReset )
		self.__pyBtnShut.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnShut.onMouseLeave.bind( self.__onBtnMouseLeave )
		self.__pyBtnShut.onLMouseDown.bind( self.__onBtnMouseLeave )
		
		self.__pyBtnSend = Button( wnd.btnSend )				#发送
		self.__pyBtnSend.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnSend.dsp = labelGather.getText( "Damagestatic:main", "open" )
		self.__pyBtnSend.onLClick.bind( self.__onSend )
		self.__pyBtnSend.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnSend.onMouseLeave.bind( self.__onBtnMouseLeave )
		self.__pyBtnSend.onLMouseDown.bind( self.__onBtnMouseLeave )
		
	# -------------------------------------------------------------------
	def setDamageStatis( self, playerID, totalDamage, totalDps ):
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		playerName = player.getName()
		playerNames = [pyStatisItem.damageInfo[0] for pyStatisItem in self.__pyListPanel.pyItems]
		if playerName in playerNames:
			for pyStatisItem in self.__pyListPanel.pyItems:
				if pyStatisItem.damageInfo[0] == playerName:
					pyStatisItem.damageInfo = ( playerName, totalDamage, totalDps )
					pyStatisItem.setStatist( playerID, totalDamage, totalDps )
					break
		else:
			item = GUI.load( "guis/general/damagestatis/statitem.gui" )
			uiFixer.firstLoadFix( item )
			pyStatisItem = StatisItem( item )
			pyStatisItem.damageInfo = ( playerName, totalDamage, totalDps )
			pyStatisItem.setStatist( playerID, totalDamage, totalDps )
			self.__pyListPanel.addItem( pyStatisItem )
		for pyStatisItem in self.__pyListPanel.pyItems:
			pyStatisItem.updateRatio()
		self.__pyListPanel.sort( key = lambda item : item.ratio, reverse = True )
		self.__pyBtnStart.visible = False
		self.__pyBtnStop.visible = True

	def __onStart( self ):
		"""
		开始接收伤害数据
		"""
		rds.damageStatistic.start()
		self.__pyListPanel.clearItems()
	
	def __onStop( self ):
		"""
		停止接受伤害数据
		"""
		rds.damageStatistic.stop()
		self.__pyBtnStop.visible = False
		self.__pyBtnStart.visible = True
	
	def __onReset( self ):
		"""
		重置伤害数据
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				rds.damageStatistic.restart()
				self.__pyListPanel.clearItems()
		showMessage( mbmsgs[0x0e51], "", MB_OK_CANCEL, query, pyOwner = self )
		return True
	
	def __onSend( self ):
		"""
		发送伤害数据
		"""
		SendWindow.instance().show( self )
	
	def __onShowTitleDsp( self, pyTitle ):
		if pyTitle is None:return
		index = pyTitle.index
		dsp = self.titles_dsp.get( index, "" )
		toolbox.infoTip.showToolTips( self, dsp )
	
	def __onHideTitleDsp( self ):
		toolbox.infoTip.hide()
	
	def __onBtnMouseEnter( self, pyBtn ):
		if pyBtn is None:return
		toolbox.infoTip.showToolTips( self, pyBtn.dsp )
	
	def __onBtnMouseLeave( self ):
		toolbox.infoTip.hide()
	
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def show( self ):
		Window.show( self )
	
	def hide( self ):
		self.__pyBtnStart.visible = True
		self.__pyBtnStop.visible = False
		Window.hide( self )

	def onLeaveWorld( self ):
		rds.damageStatistic.stop()
		self.__pyListPanel.clearItems()
		self.hide()
	
	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if StatisWindow.__instance is None:
			StatisWindow.__instance = StatisWindow()
		return StatisWindow.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return StatisWindow.__instance

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __onRecDamageStatis( SELF, playerID ):
		"""
		伤害统计数据
		"""
		damageStatis = rds.damageStatistic.statistic.get( playerID, None )
		if damageStatis is None:return
		singleDamage = damageStatis.getTotalDamage()
		totalDps = damageStatis.getDPS()
		SELF.inst.setDamageStatis( playerID, singleDamage, totalDps )
		
	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = StatisWindow
		SELF.__triggers["EVT_ON_RECEIVE_DAMAGE_STATIST"] = SELF.__onRecDamageStatis

		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )
		
# --------------------------------------------------------------------
from guis.controls.ListItem import MultiColListItem
from guis.controls.ProgressBar import HProgressBar
import csdefine

class StatisItem( MultiColListItem ):
	
	profcolor_maps = { csdefine.CLASS_FIGHTER: ( 1, 1 ),
			csdefine.CLASS_SWORDMAN: ( 2, 1 ),
			csdefine.CLASS_ARCHER: ( 3, 1 ),
			csdefine.CLASS_MAGE: ( 4, 1 )
			}

	def __init__( self, item ):
		MultiColListItem.__init__( self, item )
		self.msg = ""
		self.commonBackColor = 0, 0, 0, 255
		self.selectedBackColor = 0, 0, 0, 255
		self.highlightBackColor = 0, 0, 0, 255
		self.__pyStaticBar = HProgressBar( item.valueBar )
		self.__pyStaticBar.clipMode = "RIGHT"
		self.__pyStaticBar.value = 0.0
		self.damageInfo = ()
		self.ratio = 0.0
	
	def setStatist( self, playerID, singleDamage, totalDps ):
		caster = BigWorld.entities.get( playerID, None )
		if caster is None:return
		casterName = caster.getName()
		casterProf = caster.getClass()
		totalDamage = rds.damageStatistic.totalDamage
		if totalDamage <= 0:return
		ratio = float( singleDamage )/totalDamage
		ratioText = "%0.1f%%" % ( ratio*100 )
		self.setTextes( "%s"%casterName, "%0.1f"%singleDamage, "%0.1f"%totalDps, ratioText )
		stateMap = self.profcolor_maps.get( casterProf, ( 1, 1 ) )
		util.setGuiState( self.__pyStaticBar.getGui(), ( 4, 1 ), stateMap )
		self.__pyStaticBar.value = min( ratio, 1.0 )
		self.ratio = ratio
	
	def updateRatio( self ):
		if rds.damageStatistic.totalDamage <= 0:
			return
		self.ratio = float( self.damageInfo[1] )/rds.damageStatistic.totalDamage
		self.__pyStaticBar.value = min( self.ratio, 1.0 )
		self.pyCols[-1].text = "%0.1f%%" % ( self.ratio*100 )

StatisWindow.registerEvents()
