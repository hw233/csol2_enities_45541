# -*- coding: gb18030 -*-

from guis import *
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from ItemsFactory import SkillItem
import skills
	
class AngerPoint( RootGUI ) :
	def __init__( self ) :
		gui = GUI.load( "guis/general/spacecopyabout/spaceCopyYiJieZhanChang/angerPoint.gui" )
		uiFixer.firstLoadFix( gui )
		RootGUI.__init__( self, gui )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "MIDDLE"
		self.focus = False
		self.movable_ = False										# 不可移动
		self.escHide_ = False										# 不可按esc键关闭
		
		self.__pyItem = CastItem( gui.item, self )
		self.__pyItem.focus = True
		self.__pyItem.dragFocus = False
		self.__pyItem.dropFocus = False		
		
		self.__pyEffect = PyGUI( gui.effect )
		self.__pyEffect.visible = False
		
		self.__triggers = {}
		self.__registerTriggers()
		
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ANGER_POINT_WINDOW_SHOW"]	= self.__onShow				#显示界面
		self.__triggers["EVT_ON_ANGER_POINT_WINDOW_HIDE"]	= self.__onHide				#隐藏界面
		self.__triggers["EVT_ON_ANGER_POINT_CHANGED"]		= self.__onAngerPoint		# 玩家怒气值点改变
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
			
	#---------------------------------------------------------------------
	def playEffect( self ):
		self.__pyEffect.visible = True
		
	def stopEffect( self ):
		self.__pyEffect.visible = False
	
	def __onShow( self ):
		skillID = 123479001
#		skillID = 323175001
		itemInfo = SkillItem( skills.getSkill( skillID ) )
		self.__pyItem.update( itemInfo )
		RootGUI.show( self )
		
	def __onHide( self ):
		RootGUI.hide( self )
		
	def __onAngerPoint( self, angerPoint ):
		self.__pyItem.updateAngerPoint( angerPoint )
		
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
		
	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.hide()

class CastItem( Item ) :

	def __init__( self, item, pyBinder = None ) :
		Item.__init__( self, item.item, pyBinder )
		self.__angerPoint = 0
		
		self.__pyAmount = StaticText( item.lbAmount )
		self.__pyAmount.text = "0"
		
		self.__pyCover = PyGUI( item.cdCover.circleCover )
		self.__pyCover.visible = True
			
	 #----------------------------------------------------------------
	 #protected
	 #----------------------------------------------------------------
	def onRClick_( self, mods ) :
		Item.onRClick_( self, mods )
		if self.__angerPoint == 5:
#			self.itemInfo.spell()
			BigWorld.player().cell.yiJieUniqueSpellRequest()
		return True
	
	def onLClick_( self, mods ) :
		Item.onLClick_( self, mods )
		if self.__angerPoint == 5:
#			self.itemInfo.spell()
			BigWorld.player().cell.yiJieUniqueSpellRequest()
		return True

	 #----------------------------------------------------------------
	 #public
	 #----------------------------------------------------------------
	def update( self, itemInfo ) :
		Item.update( self, itemInfo )
		
	def updateAngerPoint( self, angerPoint ):
		self.__pyAmount.text = str( angerPoint )
		self.__angerPoint = angerPoint
		if angerPoint == 5:
			self.__pyCover.visible = False
			self.pyBinder.playEffect()
		else:
			self.__pyCover.visible = True
			self.pyBinder.stopEffect()