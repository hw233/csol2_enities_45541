# -*- coding: gb18030 -*-
#
# $Id: CommissionSale.py,fangpengjun Exp $

"""
implement CommissionSale
"""
from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ItemsPanel import ItemsPanel
from ModelPanel import ModelPanel
from LabelGather import labelGather
import GUIFacade

commiss_models = { 1:"gw1189_2",
		2:"gw1141_3",
		3:"gw1141_2",
		4:"gw1181_1",
		5:"gw1157_3",
		6:"gw1179_2",
		7:"gw1180_1",
		}

class CommissionSale( Window ):
	__instance=None
	def __init__( self ):
		assert CommissionSale.__instance is None,"CommissionSale instance has been created"
		CommissionSale.__instance=self
		wnd = GUI.load( "guis/general/commissionsale/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.canBeUpgrade_ 	 = True
		self.escHide_ 		 = True
		self.selIndex = -1
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
		self.addToMgr()
		self.onEnterWorld()

	def __initialize( self, wnd ):
		self.__pyModelsPanel = ItemsPanel( wnd.modelsPanel, wnd.scrollBar )
		self.__pyModelsPanel.viewCols = 2
		self.__pyModelsPanel.rowSpace = 8.0
		self.__pyModelsPanel.colSpace = 8.0
#		self.__pyModelsPanel.onItemSelectChanged.bind( self.__onSelectedChange )

		self.__pyCommissBtn = Button( wnd.commissBtn )
		self.__pyCommissBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCommissBtn.onLClick.bind( self.__onCommiss )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCommissBtn, "commissionsale:CommissionSale", "btnCommiss" )
		labelGather.setLabel( self.gui.expDsp, "commissionsale:CommissionSale", "stClew" )
		labelGather.setLabel( self.gui.lbTitle, "commissionsale:CommissionSale", "lbTitle" )

	@staticmethod
	def instance():
		if CommissionSale.__instance is None:
			CommissionSale.__instance=CommissionSale()
		return CommissionSale.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance of CommissionSale
		"""
		return CommissionSale.__instance

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_COMMISSION_MODEL_SELECTED"]	= self.__onModelSelected
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )
	# ---------------------------------------------------------------

	def __onModelSelected( self, index ):
		if self.selIndex != index:
			self.selIndex = index
		for pyModel in self.__pyModelsPanel.pyItems:
			pyModel.selected = pyModel.index == index

	def __onSelectedChange( self, pyModel ):
		pass

	def __onCommiss( self ):
		if self.selIndex == -1:return
		shopNamePostfix = labelGather.getText( "commissionsale:CommissionSale", "shopName" )
		BigWorld.player().cell.createTSNPC( self.selIndex, BigWorld.player().getName() + shopNamePostfix )
		self.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ):
		player = BigWorld.player()
		self.isShow=True
		for index, modelNum in commiss_models.iteritems():
			panel = GUI.load( "guis/general/commissionsale/model.gui" )
			uiFixer.firstLoadFix( panel )
			pyModel = ModelPanel( index, panel )
			pyModel.setModel( modelNum )
			self.__pyModelsPanel.addItem( pyModel )

	def onLeaveWorld( self ):
		self.selIndex = -1
		self.hide()
		self.__pyModelsPanel.clearItems()

	def show( self ):
		for pyModel in self.__pyModelsPanel.pyItems:
			pyModel.enableDrawModel()
		Window.show( self )

	def hide( self ):
		self.__deregisterTriggers()
		self.__triggers = {}
		CommissionSale.__instance=None
		self.dispose()

	def __del__(self):
		Window.__del__( self )
		if Debug.output_del_CommissionSale :
			INFO_MSG( str( self ) )