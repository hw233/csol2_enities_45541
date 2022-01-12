# -*- coding: gb18030 -*-
#
# $Id: PrestigeWindow.py,v 1.7 2008-08-30 10:09:28 wangshufeng Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabPanel
import event.EventCenter as ECenter
import GUIFacade
import csdefine

class PrestigeWindow( TabPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyTabCtrl = TabCtrl( panel.tabCtrl )
		self.__pyCreditBtn = TabButton( panel.tabCtrl.btn_0 )
		labelGather.setPyLabel( self.__pyCreditBtn, "PlayerProperty:PrestPanel", "prestige" )
		self.__pyCreditPanel = PrestigePanel( panel.tabCtrl.panel_0, self )
		self.__pyTabCtrl.addPage( TabPage( self.__pyCreditBtn, self.__pyCreditPanel ))

		self.__pyGloryBtn = TabButton( panel.tabCtrl.btn_1 )
		labelGather.setPyLabel( self.__pyGloryBtn, "PlayerProperty:PrestPanel", "honor" )
		self.__pyGloryPanel = GloryPanel( panel.tabCtrl.panel_1, self )
		self.__pyTabCtrl.addPage( TabPage( self.__pyGloryBtn, self.__pyGloryPanel ))

	def reset( self ):
		self.__pyCreditPanel.reset()
		self.__pyGloryPanel.reset()

# ----------------------------------------------------------------------------------
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.controls.StaticText import StaticText
#from guis.common.PyGUI import PyGUI
from guis.controls.ProgressBar import HProgressBar
from FactionMgr import factionMgr
import csdefine

class PrestigePanel( TabPanel ): #声望面板
	_force_list = [labelGather.getText( "PlayerProperty:PrestPanel", "positive"),
			labelGather.getText( "PlayerProperty:PrestPanel", "negative"),
			labelGather.getText( "PlayerProperty:PrestPanel", "neutrality")]

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__prestigeNodes = {}
		self.__forceTypes = {} # 势力分类
		self.__pyTvPrestiges = TreeView( panel.prestigePanel, panel.scrollBar )
		self.__pyTvPrestiges.nodeOffset = 9

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld
		self.__triggers["EVT_ON_ROLE_PRESTIGE_ADD"] = self.__onAddRolePrestige
		self.__triggers["EVT_ON_ROLE_PRESTIGE_UPDATE"] = self.__onUpdateRolePrestige
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ---------------------------------------------------------------------
	def __onRoleEnterWorld( self, player ):	# wsf
		DEBUG_MSG( player.prestige )
		for factionID in player.prestige:
			ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_ADD", factionID )

	def __onAddRolePrestige( self, factionID ):
		player = BigWorld.player()
		if self.__prestigeNodes.has_key( factionID ):return
		force = factionMgr.getForce( factionID )
		if force not in self._force_list:return #未知势力
		pyPreNode = PrestigeNode()
		pyPreNode.updateInfo( factionID )
		self.__prestigeNodes[factionID ] = pyPreNode
		if not self.__forceTypes.has_key( force ):
			typeNode = ForceNode()
			typeNode.text = force
			self.__forceTypes[force] = typeNode
			typeNode.pyNodes.add( pyPreNode )
		else:
			typeNode = self.__forceTypes[force]
			typeNode.pyNodes.add( pyPreNode )
		self.__pyTvPrestiges.pyNodes.add( typeNode )

	def __onUpdateRolePrestige( self, factionID ):
		player = BigWorld.player()
		if not self.__prestigeNodes.has_key( factionID ):
			ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_ADD", factionID )
			return
		pyPreNode = self.__prestigeNodes[factionID]
		pyPreNode.updateInfo( factionID )
	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def reset( self ):
		self.__prestigeNodes = {}
		self.__forceTypes = {} # 势力分类
		self.__pyTvPrestiges.pyNodes.clear()

# -------------------------------------------------------------------------------
class PrestigeNode( TreeNode ):
	pre_states = { csdefine.PRESTIGE_ENEMY : (( 1,1 ), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_enemy"),( -39000, -3000 )),
			csdefine.PRESTIGE_STRANGE : (( 1, 2), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_strange"), ( -3000, 0)),
			csdefine.PRESTIGE_NEUTRAL :(( 2, 1), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_neutral"), ( 0, 3000 )),
			csdefine.PRESTIGE_FRIENDLY :(( 2, 2 ), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_friendly"),( 3000, 9000 )),
			csdefine.PRESTIGE_RESPECT : (( 3, 1 ), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_respect"),( 9000, 21000 )),
			csdefine.PRESTIGE_ADMIRE :(( 3,1 ), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_admire"), ( 21000, 42000 )),
			csdefine.PRESTIGE_ADORE :((3, 1), labelGather.getText( "PlayerProperty:PrestPanel", "prestige_adore"), ( 42000, 45000 ))
			}
	pre_colors = { csdefine.PRESTIGE_ENEMY : ( 218, 0, 0, 255 ),
			csdefine.PRESTIGE_STRANGE : ( 255, 93, 21, 255 ),
			csdefine.PRESTIGE_NEUTRAL : ( 242, 217, 91, 255 ),
			csdefine.PRESTIGE_FRIENDLY :( 154, 237, 94, 255 ),
			csdefine.PRESTIGE_RESPECT : ( 0, 183, 4, 255 ),
			csdefine.PRESTIGE_ADMIRE : ( 0, 183, 4, 255 ),
			csdefine.PRESTIGE_ADORE : ( 0, 183, 4, 255 ),
		}

	def __init__( self ):
		node = GUI.load( "guis/general/playerprowindow/creditpanel/prestigenode.gui" )
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node )
		self.selectable = False
		self.canBeHighlight = False
		self.__pyStCredit = StaticText( node.node.stCredit )
		self.__pyStLevel = StaticText( node.node.stLevel )
#		self.__pyColorBg = PyGUI( node.node.colorBg )
		self.__pyColorBar = HProgressBar( node.node.colorBar )
		self.__pyColorBar.clipMode = "RIGHT"
		self.autoWidth = False							# 节点不会自适应文本的宽度（hyw -- 2008.11.15）

	def updateInfo( self, factionID ): #开启声望初始化
		player = BigWorld.player()
		preLevel = player.getPretigeLevel( factionID )
		name = factionMgr.getName( factionID )
		value = player.getPrestige( factionID )
		self.text = name
		value1 = value - self.pre_states[preLevel][2][0]
		value2 = self.pre_states[preLevel][2][1] - self.pre_states[preLevel][2][0]
		self.__pyStCredit.text = "%d/%d"%( value1, value2 )
		if self.pre_states.has_key( preLevel ):
			self.__pyStLevel.text = self.pre_states[preLevel][1]
			self.__pyStLevel.color = self.pre_colors[preLevel]
#			util.setGuiState( self.__pyColorBg.getGui(), ( 3, 2 ), self.pre_states[preLevel][0] )
			util.setGuiState( self.__pyColorBar.getGui(), ( 3, 2 ), self.pre_states[preLevel][0] )
			self.__pyColorBar.value = float( value1 )/value2


class ForceNode( TreeNode ) :

	def __init__( self ) :
		node = GUI.load( "guis/general/playerprowindow/creditpanel/typenode.gui" )
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node )
		self.autoWidth = False
		self.highlightForeColor = self.commonForeColor
		self.selectedForeColor = self.commonForeColor

class GloryPanel( TabPanel ): #荣誉面板
	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel )
		pass

	def reset( self ):
		pass