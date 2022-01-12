# -*- coding: gb18030 -*-
#
# $Id: YaYuTowers.py

"""
imlement YaYuTowers window
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from config.client.msgboxtexts import Datas as mbmsgs
from AbstractTemplates import Singleton
import GUIFacade
import csdefine
import BigWorld
import Timer

class YaYuTowers( Singleton, RootGUI ) :
	"""
	猰貐防御塔
	"""
	__triggers = {}
	_cc_tower_cls = ["20244001", "20244002", "20244003"]

	def __init__( self ) :
		wnd = GUI.load( "guis/general/yayutowers/window.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.focus= False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_  = False
		self.__towers = {}
		self.__isVisible = False
		self.__querycbid = 0
		self.__freshcbid = 0
		self.__initialize( wnd )
		self.addToMgr( "yayuTowers" )

	def __initialize( self, wnd ) :
		self.__pyArray = PyGUI( wnd.arrayPanel )

		self.__pyShowBtn = Button( wnd.showBtn )
		self.__pyShowBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyShowBtn.onLClick.bind( self.__showArray )
		self.__pyShowBtn.visible = False
		
		self.__pyHideBtn = Button( wnd.hideBtn )
		self.__pyHideBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyHideBtn.onLClick.bind( self.__hideArray )
		self.__pyHideBtn.visible = False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""
		布局防御塔头像
		"""
		if len( self.__towers ) == 0 : return
		pyFirstBox = self.__towers.values()[0]
		pyFirstBox.left = 0.0
		pyFirstBox.top = 0.0
		top = 0.0
		for index, pyBox in enumerate( self.__towers.values() ) :
			if index == 0: continue
			pyAboveBox = self.__towers.values()[index-1]  #上一个队友头像
			pyBox.left = pyFirstBox.left
			pyBox.top = top + pyBox.height
			top = pyBox.top
		pyLastBox = self.__towers.values()[-1]
		self.__pyArray.width = pyLastBox.right
		self.__pyArray.height = pyLastBox.bottom
		self.width = self.__pyArray.width
		self.height = self.__pyArray.bottom

	# -------------------------------------------------
	def __showArray( self ) :
		self.__pyArray.visible = True
		self.__pyShowBtn.visible = False
		self.__pyHideBtn.visible = True

	def __hideArray( self ) :
		self.__pyArray.visible = False
		self.__pyHideBtn.visible = False
		self.__pyShowBtn.visible = True

	# -------------------------------------------------
	def __addTower( self, entity ) :
		if id in self.__towers:return
		box = GUI.load( "guis/general/yayutowers/towerbox.gui")
		uiFixer.firstLoadFix( box )
		pyBox = TowerBox( box, entity, self )
		self.__pyArray.addPyChild( pyBox )
		self.__towers[entity.id] = pyBox
		self.__layout()

	def __queryTower( self ):
		if len( self.__towers ) >= len( self._cc_tower_cls ):
			self.__pyHideBtn.visible = True
			if self.__freshcbid:
				Timer.cancel( self.__freshcbid )
				self.__freshcbid = 0
			self.__freshcbid = Timer.addTimer( 0, 1.0, self.__freshTower )
			BigWorld.cancelCallback( self.__querycbid )
			self.__querycbid = 0
			return
		for id, entity in BigWorld.entities.items():
			if hasattr( entity, "className" ) and \
			entity.className in self._cc_tower_cls:
				self.__addTower( entity )
		self.__querycbid = BigWorld.callback( 1.0, self.__queryTower )
	
	def __freshTower( self ):
		"""
		刷新防御塔状态
		"""
		for towerID, pyTower in self.__towers.items():
			tower = BigWorld.entities.get( towerID )
			if tower is None:continue
			name = tower.getName()
			hp = tower.HP
			hpMax = tower.HP_Max
			pyTower.onUpdateInfo( name, hp, hpMax )

	@classmethod
	def __onEnterYaYuCopy( SELF ) :
		SELF.inst.onEnterYaYuCopy()

	@classmethod
	def __onLeaveYaYuCopy( SELF ) :
		SELF.inst.onLeaveYaYuCopy()

	@classmethod
	def __onTowerHPChange( SELF, id, hp, hpMax ) :
		SELF.inst.onTowerHPChange( id, hp, hpMax )

	@classmethod
	def __onYaYuTowerDestroy( SELF ) :
		SELF.inst.onYaYuTowerDestroy()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterYaYuCopy( self ):
		"""
		进入拯救猰貐副本
		"""
		player = BigWorld.player()
		self.__querycbid = BigWorld.callback( 3.0, self.__queryTower )
		self.show()
	
	def onLeaveYaYuCopy( self ):
		"""
		离开拯救猰貐副本
		"""
		self.hide()
		for pyTower in self.__towers.values() :
			pyTower.dispose()
		self.__towers = {}
	
	def onTowerHPChange( self, id, hp, hpMax ):
		"""
		防御塔血量变化
		"""
		pyTower = self.__towers.get( id, None )
		if pyTower is None:return
		pyTower.onUpdateHP( hp, hpMax )
	
	def onLeaveWorld( self ) :
		self.hide()
		for pyTower in self.__towers.values() :
			pyTower.dispose()
		self.__towers = {}

	def show( self ):
		RootGUI.show( self )
	
	def hide( self ):
		RootGUI.hide( self )
		self.dispose()
		self.removeFromMgr()
		Timer.cancel( self.__freshcbid )
		self.__freshcbid = 0

	def dispose( self ) :
		RootGUI.dispose( self )
		self.__class__.releaseInst()

	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_OPEN_SPACE_TOWER_INTERFACE"] = SELF.__onEnterYaYuCopy
		SELF.__triggers["EVT_ON_CLOSE_SPACE_TOWER_INTERFACE"] = SELF.__onLeaveYaYuCopy
		SELF.__triggers["EVT_ON_YAYU_TOWER_HP_CHANGE"] = SELF.__onTowerHPChange
		SELF.__triggers["EVT_ON_YAYU_TOWER_DES"] = SELF.__onYaYuTowerDestroy
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )
			
	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[evtMacro]( *args )

# ------------------------------------------------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.Icon import Icon
from guis.controls.ProgressBar import HProgressBar as ProgressBar

class TowerBox( Control ):
	"""
	防御塔头像
	"""
	def __init__( self, box, entity, pyBinder = None ):
		Control.__init__( self, box, pyBinder )
		self.focus = True
		self.tower = entity
		self.__initialize( box, entity )

	def __del__( self ) :
		if Debug.output_del_TowerBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Control.dispose( self )
		
	def __initialize( self, box, entity ):
		self.__pyHeader = PyGUI( box.header )
		self.__pyLbName = StaticText( box.lbName )
		self.__pyHeader.texture = entity.getHeadTexture()
		self.__pyLbName.text = entity.getName()
		
		self.__pyLbLevel = StaticText( box.lbLevel )
		self.__pyLbLevel.fontSize = 12
		self.__pyLbLevel.text = str( entity.level )
		self.__pyLbLevel.h_anchor = 'CENTER'
			
		self.__pyHPBar = ProgressBar( box.hpBar )
		self.__pyHPBar.clipMode = "RIGHT"
		
		self.__pyLbHP = StaticText( box.lbHP )
		self.__pyLbHP.fontSize = 11
		self.__pyLbHP.h_anchor = 'CENTER'
		
		self.__pyCaptainMark = PyGUI( box.captainMark )
		self.__pyCaptainMark.visible = False

		self.__pyClassMark = Icon( box.classMark )
		self.__pyClassMark.visible = False
	
	def onUpdateInfo( self, name, hp, hpMax ):
		rate = 0.0
		if name != "" and \
		self.__pyLbName.text == "":
			self.__pyLbName.text = name
		if hpMax == 0: 
			rate = 1
			self.pyLbHP_.text = "???/???"
		else:
			rate = float( hp  ) / hpMax
			self.__pyLbHP.text = "%d/%d" % ( hp, hpMax )
		self.__pyHPBar.value = rate
		if rate == 0.0:						#已被摧毁
			self.tower = None
			self.focus = False
			for n, ch in self.getGui().children :
				ch.materialFX = "COLOUR_EFF"

	def onLClick_( self, mods ):
		"""
		点击头像，选取防御塔
		"""
		Control.onLClick_( self, mods )
		if self.tower:
			try:
				entity = BigWorld.entities[self.tower.id]
			except:
				return
			rds.targetMgr.bindTarget( entity )

YaYuTowers.registerTriggers()