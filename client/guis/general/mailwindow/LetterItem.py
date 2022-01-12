# -*- coding: gb18030 -*-
#
# $Id: LetterItem.py,v 1.7 2008-08-25 07:06:39 huangyongwei Exp $

"""
implement ware item
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.ListItem import ListItem
from ItemsFactory import ObjectItem as ItemInfo
from guis.MLUIDefine import ItemQAColorMode
import event.EventCenter as ECenter
import GUIFacade
import csstatus
from Time import Time
from bwdebug import *

class LetterItem( Control ):

	_cc_destroy_time = 7*24*3600

	def __init__( self, pyBinder = None ):
		letter = GUI.load( "guis/general/mailwindow/letter.gui" )
		uiFixer.firstLoadFix( letter )
		Control.__init__( self, letter )
		self.crossFocus = False
		self.dragFocus = False
		self.focus = False
		self.mailID = -1
		self.mailType = -1
		self.__panelState = ( 1, 1 )

		self.__pyItem = Item( letter.item, self ) #信件第一个物品图标

		self.__pyStName = StaticText( letter.stName )
		self.__pyStName.text = ""

		self.__pyStTitle = StaticText( letter.stTitle )
		self.__pyStTitle.text = ""

		self.__pyStTime = StaticText( letter.stTime )
		self.__pyStTime.text = ""

		self.__pyStContent = StaticText( letter.stContent )
		self.__pyStContent.text = ""

		self.infoPanel = letter.infoPanel
		self.readedTime = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ):
		if self.selected:return		
		if self.readedTime != 0:
			self.panelState = ( 2, 1 )
		else: self.panelState = ( 4, 1 )	
		self.__pyItem.selected = True

	def __deselect( self ):
		if self.readedTime != 0:
			self.panelState = ( 1, 1 )
		else:self.panelState = ( 3, 1 )	
		self.__pyItem.selected = False

	# -----------------------------------------------------------
	# public
	# -----------------------------------------------------------
	def reset( self ) :
		"""
		resume common state
		"""
		self.selected = False
		self.update( None )

	def update( self, letter ):
		if letter is not None:
			self.__pyStName.text = letter["senderNamer"]
			try:
				self.__pyStTitle.text = letter["title"]
			except:
				BigWorld.player().statusMessage( csstatus.MAIL_TITLE_OR_CONTENT_TOO_LONG, letter["mailID"] )
			receiveTime = letter["receiveTime"]
			self.readedTime = letter["readedTime"]
			items = letter["items"]
			money = letter["money"]
			mailID = letter["mailID"]
			mailType = letter["senderType"] #邮件类型
			self.mailID = mailID
			self.mailType = mailType
			if self.readedTime !=0: # 已经读过,
				if self.isHasItem( items ) or money > 0: #物品或金钱未取出
					remainTime = self._cc_destroy_time + receiveTime - Time.time()
					if remainTime > self._cc_destroy_time: #如果剩余时间大于7天，则按7天算
						remainTime = self._cc_destroy_time
					remainDays = remainTime/( 24*3600 )
					remainHours = ( remainTime%( 24*3600 ) )/3600
					timeText = labelGather.getText( "MailWindow:panel_0", "remainDays" )%( remainDays, remainHours )
				else: #物品已取出
					remainTime = 2*3600 + self.readedTime - Time.time()
					remainHours = remainTime/3600
					remMins = ( remainTime%3600 )/60
					timeText = labelGather.getText( "MailWindow:panel_0", "remainHours" )%( remainHours, remMins )
				self.__pyStTitle.color = (150,150,150,255 )  # 已阅邮件标题颜色改为灰白
				self.__pyStName.color = (40,175,150,255 )  
				self.__pyStTime.color = (40,175,150,255 )
			else: # 未读，保存时间为7天
				remainTime = self._cc_destroy_time + receiveTime - Time.time()
				remainDays = remainTime/( 24*3600 )
				remainHours = ( remainTime%( 24*3600 ) )/3600
				timeText = labelGather.getText( "MailWindow:panel_0", "remainDays" )%( remainDays, remainHours )
				self.__pyStTitle.color = (255,255,255,255 )  
				self.__pyStName.color = (40,233,212,255 )  # 未读邮件标题发件者名字颜色高亮
				self.__pyStTime.color = (40,233,212,255 )  # 未读邮件标题剩余时间颜色高亮
			self.__pyStTime.text = timeText
			itemInfo = None
			firstItem = self.getFirstItem( items )
			if firstItem is not None:
				# 有物品，则显示第一个物品图标
				itemInfo = ItemInfo( firstItem ) #显示第一个物品图标
			else:										
				# 无物品
				if money > 0:
					# 有金钱，则显示金钱图标
					moneyItem = BigWorld.player().createDynamicItem( 60101001 ) #金钱实例
					itemInfo = ItemInfo( moneyItem )
			self.__pyItem.update( itemInfo, mailID )
		else:
			self.__pyStName.text = ""
			self.__pyStTitle.text = ""
			self.__pyStTime.text = ""
			self.__pyItem.update( None, -1 )
			self.__pyItem.selected = False    #改变删除了的邮件的物品图标还是保持选择状态的BUG
			self.panelState = ( 1, 1 )
			self.mailID = -1
		

	def getFirstItem( self, items ):
		"""
		获取邮件中第一个物品
		"""
		for item in items.itervalues():
			if item is not None:
				return item
		return None

	def isHasItem( self, items ):
		"""
		是否含有物品
		"""
		for item in items.itervalues():
			if item is None:continue
			return True
		return False

	# -------------------------------------------------------------------------
	#
	# -------------------------------------------------------------------------
	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getPanelState( self ):		
		return self.__panelState
		
	def _setPanelState( self, state ):
		elements = self.infoPanel.elements
		self.__panelState = state
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R4C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )
				
	selected = property( _getSelected, _setSelected )
	panelState = property( _getPanelState, _setPanelState )

# -------------------------------------------------------------
# 邮件物品格子
# -------------------------------------------------------------
class Item( PyGUI ):

	def __init__( self, item, pyBinder ):
		PyGUI.__init__( self, item )
		self.pyBinder = pyBinder
		self.__selected = False
		self.__pyItem = InfoItem( item.item, pyBinder )
		self.__pyCover = PyGUI( item.cover )
		self.__pyStAmount = StaticText( item.item.lbAmount )
		self.__pyCover.visible = False

	def __select( self ):
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		if self.__pyCover:
			self.__pyCover.visible = False

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	def update( self, itemInfo, mailID ):
		self.__pyItem.update( itemInfo, mailID )
		if itemInfo is not None: #有物品
			quality = itemInfo.quality
			self.__setItemQuality( self.getGui(), quality )
			self.__pyItem.crossFocus = True
		else:
			if mailID != -1: #没有物品，但有信件
				self.__setItemQuality( self.getGui(), 1 )
				self.__pyItem.icon = ( "icons/tb_rw_xfeng_003.dds", ((0.0, 0.0), (0.0, 0.5625), (0.5625, 0.5625), (0.5625, 0.0))) #显示信封
				self.__pyItem.crossFocus = True
			else: #两者都没有
				self.__setItemQuality( self.getGui(), 0 )
				self.__pyItem.crossFocus = False
				self.__pyItem.selected = False

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected
	selected = property( _getSelected, _setSelected )

# -------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem

class InfoItem( BOItem ):

	def __init__( self, infoItem, pyBinder = None ):
		BOItem.__init__( self, infoItem, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.selectable = True
		self.mailID = -1
		self.mailType = -1

	def subclass( self, item, pyBinder ) :
		BOItem.subclass( self, item, pyBinder )
		return True

	def dispose( self ) :
		BOItem.dispose( self )

	def onMouseEnter_( self ):
		BOItem.onMouseEnter_( self )
		if self.itemInfo is None and self.mailID == -1:return
		if self.pyBinder.readedTime != 0 :
			self.pyBinder.panelState = ( 2, 1 )
		else: self.pyBinder.panelState = ( 4, 1 )
		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.itemInfo is None and self.mailID == -1:return
		if self.pyBinder.selected:return
		if self.pyBinder.readedTime != 0 :
			self.pyBinder.panelState = ( 1, 1 )
		else: self.pyBinder.panelState = ( 3, 1 )
		return True

	def onLClick_( self, mods ):
		if not self.itemInfo and self.mailID == -1: return
		BOItem.onLClick_( self, mods )
		ECenter.fireEvent( "EVT_ON_MAIL_SELECTED", self.mailID )
		return True

	def onLDBClick_( self, mods ):
		if not self.itemInfo and self.mailID == -1: return
		BOItem.onLClick_( self, mods )
		BigWorld.player().mail_read( self.mailID )
		return True

	def onDragStart_( self, pyDragged ) :
		Control.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True

	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, itemInfo, mailID ) :
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		self.mailID = mailID
		#if itemInfo is not None:
		#	self.description = itemInfo.description				# 底层已经做了这步工作，这里不需要再做一次。