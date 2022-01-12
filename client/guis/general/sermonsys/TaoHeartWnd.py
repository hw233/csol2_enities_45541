# -*- coding: gb18030 -*-
#
# $Id: TaoHeartWnd.py, fangpengjun Exp $
"""
implement TaoHeartWnd class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Button import Button
from guis.controls.Item import Item
from AbstractTemplates import Singleton
from TaoHeartRender import TaoHeartRender
from config.client.msgboxtexts import Datas as mbmsgs
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import csdefine
import skills
from ZDDataLoader import *
daofaLoader = DaofaDataLoader.instance()
daofaDatas = daofaLoader._datas
from TaofaLocker import TaofaLocker
from guis.MLUIDefine import ItemQAColorMode
from guis.MLUIDefine import QAColor
import ItemTypeEnum
import event.EventCenter as ECenter

class TaoHeartWnd( Singleton, Window ):
	"""
	道心窗口
	'"""
	__triggers = {}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/sermonsys/taoheartwnd/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.pySelItem = None
		self.__pyComBox = None
		self.__initialize( wnd )
		self.addToMgr( "taoHeartWnd" )
	
	def __initialize( self, wnd ):
		self.__pyThEquips = {}
		self.__pyThItems = {}
		equipsPanel = wnd.equipsPanel
		itemsPanel = wnd.itemsPanel
		for name, item in equipsPanel.children:
			if name.startswith( "thEquip_" ):					#角色身上道心
				index = int( name.split( "_" )[1] )
				pyThEquip = TaoHeartItem( item, csdefine.KB_EQUIP_DAO_XIN_ID, index, DragMark.SERMON_EQUIP_WND )
				pyThEquip.update( None )
				self.__pyThEquips[index] = pyThEquip
		for name, item in itemsPanel.children:
			if name.startswith( "thItem_" ):					#道心存储物品
				index = int( name.split( "_" )[1] )
				pyThItem = TaoHeartItem( item, csdefine.KB_COM_DAO_XIN_ID, index, DragMark.SERMON_COMMON_WND )
				pyThItem.update( None )
				self.__pyThItems[index] = pyThItem
		self.__modelRender = TaoHeartRender( wnd.modelRender )
		
		self.__pyBtnComp = HButtonEx( wnd.btnComp )
		self.__pyBtnComp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnComp.onLClick.bind( self.__onCompose )
		labelGather.setPyBgLabel( self.__pyBtnComp, "SermonSys:SemonWnd", "compose" )
		
		self.__pyBtnLock = HButtonEx( wnd.btnLock )
		self.__pyBtnLock.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLock.enable = True
		self.__pyBtnLock.onLClick.bind( self.__onLock )
		labelGather.setPyBgLabel( self.__pyBtnLock, "SermonSys:TaoHeart", "locking" )
		
		self.__pyBtnSermon = HButtonEx( wnd.btnSermon )
		self.__pyBtnSermon.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSermon.onLClick.bind( self.__onSermon )
		labelGather.setPyBgLabel( self.__pyBtnSermon, "SermonSys:TaoHeart", "semon" )
		
		self.__pyDfLocker = TaofaLocker()
		
		labelGather.setPyLabel( self.pyLbTitle_, "SermonSys:TaoHeart", "title" )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __onCompose( self, pyBtn ):
		"""
		一键合成
		"""
		if pyBtn is None:return
		BigWorld.player().autoCompose( csdefine.KB_COM_DAO_XIN_ID )
	
	def __onLock( self, pyBtn ):
		"""
		锁定
		"""
		if pyBtn is None:return
		self.__pyDfLocker.enterLocking( pyBtn )
	
	def __onSermon( self, pyBtn ):
		"""
		弹出证道窗口
		"""
		sermWnd = rds.ruisMgr.sermonWnd
		sermWnd.show()
	
	def __getCurActOrder( self, daoxinID ):
		"""
		获取已激活道心格子数
		"""
		for grid in BigWorld.player().activeGrid:
			if grid["daoXinID"] == daoxinID:
				return grid["actOrder"]
		return -1
		
	@classmethod
	def __onAddDaoFa( SELF, daoxinID, orderID, uid ):
		"""
		增加道法
		"""
		self = SELF.inst
		player = BigWorld.player()
		daofa = player.uidToDaofa( uid )
		if daoxinID == csdefine.KB_COM_DAO_XIN_ID:              #道心普通包裹
			pyThItem = self.__pyThItems.get( orderID, None )
			if pyThItem is None:return
			pyThItem.update( daofa )
		elif daoxinID == csdefine.KB_EQUIP_DAO_XIN_ID:		#道心装备包裹
			pyEqtem = self.__pyThEquips.get( orderID, None )
			if pyEqtem is None:return
			pyEqtem.update( daofa )
		
	@classmethod
	def __onRemoveDaoFa( SELF, daoxinID, orderID, uid, isPickup ):
		"""
		移除道法
		"""
		self = SELF.inst
		if daoxinID == csdefine.KB_COM_DAO_XIN_ID:              #道心普通包裹
			for index, pyThItem in self.__pyThItems.items():
				daofa = pyThItem.daofa
				if daofa is None:continue
				if daofa.uid == uid:
					pyThItem.update( None )
		elif daoxinID == csdefine.KB_EQUIP_DAO_XIN_ID:		#道心装备包裹
			for index, pyEqItem in self.__pyThEquips.items():
				daofa = pyEqItem.daofa
				if daofa is None:continue
				if daofa.uid == uid:
					pyEqItem.update( None )
	
	@classmethod
	def __onActiveGridCost( SELF, orderID, yuanbao ):
		"""
		激活锁定格子花费
		"""
		self = SELF.inst
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().confirmActiveGrid( orderID )
		showMessage( mbmsgs[0x10a1] %yuanbao , "", MB_OK_CANCEL, query )
		return True
		
	@classmethod
	def __onActiveGridResult( SELF, daoxinID, orderID, result ):
		"""
		激活锁定格子结果
		"""
		self = SELF.inst
		if result:
			for order in range( orderID + 1 ):
				pyGrid = None
				if daoxinID == csdefine.KB_COM_DAO_XIN_ID:
					pyGrid = self.__pyThItems.get( order, None )
				elif daoxinID == csdefine.KB_EQUIP_DAO_XIN_ID:
					pyGrid = self.__pyThEquips.get( order, None )
				if pyGrid is None:continue
				if pyGrid.actived:continue
				pyGrid.actived = True
		else:
			showMessage( mbmsgs[0x10a2] , "", MB_OK, None )
			return True
			
	@classmethod
	def __onCompConfirm( SELF, srcUID, dstUID, exp ):
		"""
		合成确认
		"""
		self = SELF.inst
		player = BigWorld.player()
		srcDaofa = player.uidToDaofa( srcUID )
		dstDaofa = player.uidToDaofa( dstUID )
		dstName = dstDaofa.getName()
		srcName = srcDaofa.getName()
		def query( rs_id ):
			if rs_id == RS_OK:
				player.confirmComposeDaofa( srcUID, dstUID )
		if not self.__pyComBox is None:
			self.__pyComBox.visible = False
			self.__pyComBox = None
		self.__pyComBox = showMessage( mbmsgs[0x10a4] %( dstName, srcName, exp ) , "", MB_OK_CANCEL, query )
		return True

	@classmethod
	def __onDaoXinSelected( SELF, uid ):
		"""
		选择某个道心
		"""
		self = SELF.inst
		pyThItems = self.__pyThItems.values()
		pyThItems.extend( self.__pyThEquips.values() )
		for pyThItem in pyThItems:
			daofa = pyThItem.daofa
			if daofa is None:continue
			pyThItem.selected = daofa.uid == uid
			if daofa.uid == uid:
				self.pySelItem = pyThItem
		self.__pyBtnLock.enable = self.pySelItem is not None
		if self.pySelItem:
			daofa = self.pySelItem.daofa
			if daofa is None:return
			isLocked = daofa.isLocked
			if isLocked:
				labelGather.setPyBgLabel( self.__pyBtnLock, "SermonSys:TaoHeart", "unlocking" )
			else:
				labelGather.setPyBgLabel( self.__pyBtnLock, "SermonSys:TaoHeart", "locking" )

	@classmethod
	def __onLockDaofa( SELF, daofa ):
		"""
		锁定/锁定道法
		"""
		self = SELF.inst
		uid = daofa.uid
		daoxinID = daofa.daoXinID
		lockDaofa = None
		isLocked = False
		player = BigWorld.player()
		pyThItems = self.__pyThItems.values()
		pyThItems.extend( self.__pyThEquips.values() )
		for pyThItem in pyThItems:
			daofaItem = pyThItem.daofa
			if daofaItem is None:continue
			if daofaItem.uid == uid:
				pdf = player.uidToDaofa( uid )
				isLocked = pdf.isLocked
				pyThItem.lock( isLocked )
				lockDaofa = pdf
		pySelItem = self.pySelItem
		if pySelItem is None:return
		selDaofa = pySelItem.daofa
		if lockDaofa and selDaofa and \
		selDaofa.uid == lockDaofa.uid:
			if isLocked:
				labelGather.setPyBgLabel( self.__pyBtnLock, "SermonSys:TaoHeart", "unlocking" )
			else:
				labelGather.setPyBgLabel( self.__pyBtnLock, "SermonSys:TaoHeart", "locking" )

	@classmethod
	def __onDaoFaChanged( SELF, daofa ):
		"""
		道法属性改变
		"""
		self = SELF.inst
		uid = daofa.uid
		player = BigWorld.player()
		pyThItems = self.__pyThItems.values()
		pyThItems.extend( self.__pyThEquips.values() )
		for pyThItem in pyThItems:
			daofaItem = pyThItem.daofa
			if daofaItem is None:continue
			if daofaItem.uid == uid:
				pyThItem.update( daofa )
				
	@classmethod
	def __onAutoCompConf( SELF, daoxinID, uid ):
		"""
		一键合成确认回调
		"""
		self = SELF.inst
		if daoxinID != csdefine.KB_COM_DAO_XIN_ID:
			return
		player = BigWorld.player()
		daofa = player.uidToDaofa( uid )
		msg = ""
		mbType = MB_OK_CANCEL
		if uid > 0:
			dfName = daofa.name
			msg = mbmsgs[0x10ac]%dfName
		else:
			msg = mbmsgs[0x10ad]
			mbType = MB_OK
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().confirmAutoCompose( csdefine.KB_COM_DAO_XIN_ID )
		showMessage( msg, "", mbType, query, self )
		return True
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_SERMON_ADD_DAOFA"] = SELF.__onAddDaoFa
		SELF.__triggers["EVT_ON_SERMON_REMOVE_DAOFA"] = SELF.__onRemoveDaoFa
		SELF.__triggers["EVT_ON_SERMON_ACTIVE_GRID_COST"] = SELF.__onActiveGridCost
		SELF.__triggers["EVT_ON_SERMON_ACTIVE_GRID_RESULT"] = SELF.__onActiveGridResult
		SELF.__triggers["EVT_ON_SERMON_COMPOSE_DAOFA_CONFIRM"] = SELF.__onCompConfirm
		SELF.__triggers["EVT_ON_SERMON_DAOXIN_SELECTED"] = SELF.__onDaoXinSelected
		SELF.__triggers["EVT_ON_SERMON_LOCK_DAOFA"] = SELF.__onLockDaofa
		SELF.__triggers["EVT_ON_SERMON_DAOFA_CHANGED"] = SELF.__onDaoFaChanged
		SELF.__triggers["EVT_ON_SERMON_AUTO_COMPOSE_CONFIRM"] = SELF.__onAutoCompConf
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )
	
	def onLeaveWorld( self ) :
		for pyThEquip in self.__pyThEquips.values():
			pyThEquip.actived = False
			pyThEquip.update( None )
		for pyThItem in self.__pyThItems.values():
			pyThItem.actived = False
			pyThItem.update( None )
		self.pySelItem = None
		self.__pyComBox = None
		self.hide()

	def onEnterWorld( self ) :
		self.__modelRender.onEnterWorld()
		Window.onEnterWorld( self )
	
	def show( self ):
		player = BigWorld.player()
		self.__modelRender.enableDrawModel()
		for grid in player.activeGrid:
			dxID = grid["daoXinID"] 
			orders = grid["actOrder"]
			if dxID == csdefine.KB_COM_DAO_XIN_ID:
				for order in range( orders + 1 ):
					pyThItem = self.__pyThItems.get( order, None )
					if pyThItem is None:continue
					pyThItem.actived = True
			elif dxID == csdefine.KB_EQUIP_DAO_XIN_ID:
				for order in range( orders + 1 ):
					pyThEquip = self.__pyThEquips.get( order, None )
					if pyThEquip is None:continue
					pyThEquip.actived = True
		self.__modelRender.resetModel()
		Window.show( self )
	
	def hide( self ):
		self.__modelRender.disableDrawModel()
		Window.hide( self )

TaoHeartWnd.registerTriggers()
# ----------------------------------------------------------------------------

from guis.controls.Icon import Icon
class TaoHeartItem( PyGUI ):
	"""
	道心格子
	"""
	def __init__( self, item, daoxinID, orderID, dragMark ):
		PyGUI.__init__( self, item )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True
		self.daoxinID = daoxinID
		self.orderID = orderID
		self.__pyItem = Item( item.item, daoxinID, orderID, dragMark, self )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyItemFrm = PyGUI( item.itemFrm )
		self.__pyLock = PyGUI( item.lock )
		self.__actived = False
		self.__selected = False
		self.isLocked = False

	def update( self, daofa ):
		"""
		更新道心
		"""
		self.__pyItem.update( daofa )
		if daofa is None:
			self.selected = False
	
	def onMouseEnter( self, dragMark ):
		"""
		鼠标进入子物品被调用
		"""
		if self.__selected:return
		util.setGuiState( self.__pyItemFrm.getGui(), ( 1, 2 ), ( 1, 2 ) )
	
	def onMouseLeave( self, dragMark ):
		"""
		鼠标离开子物品被调用
		"""
		if self.__selected:return
		util.setGuiState( self.__pyItemFrm.getGui(), ( 1, 2 ), ( 1, 1 ) )
	
	def lock( self, isLocked ):
		"""
		锁定/解锁道法
		"""
		self.isLocked = isLocked
		self.__pyItem.lock( isLocked )
	
	def _getActived( self ):
		"""
		"""
		return self.__actived
	
	def _setActived( self, actived ):
		"""
		激活格子
		"""
		self.__actived = actived
		self.__pyLock.visible = not actived

	def _getDaofa( self ):
		"""
		"""
		return self.__pyItem.daofa
	
	def _getSelected( self ):
		return self.__selected
	
	def _setSelected( self, selected ):
		self.__selected = selected
		if selected:
			util.setGuiState( self.__pyItemFrm.getGui(), ( 1, 2 ), ( 1, 2 ) )
		else:
			util.setGuiState( self.__pyItemFrm.getGui(), ( 1, 2 ), ( 1, 1 ) )
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	actived = property( _getActived, _setActived )
	daofa = property( _getDaofa,  )
	selected = property( _getSelected, _setSelected )

# -------------------------------------------------------------------------------
class Item( Control ):
	"""
	道心物品
	"""
	def __init__( self, item, daoxinID, orderID, dragMark, pyBinder = None ):
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = False
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True
		self.daoxinID = daoxinID
		self.orderID = orderID
		self.dragMark = dragMark
		self.__pyIcon = Icon( item.icon )
		self.__pyIcon.visible = True
		self.__pyIcon.focus = True
		self.__pyIcon.crossFocus = True
		self.__pyIcon.onLClick.bind( self.__onIconLClick )
		self.__pyIcon.onRClick.bind( self.__onIconRClick )
		self.__pyIcon.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyIcon.onMouseLeave.bind( self.__onMouseLeave )

		self.__pyStName = StaticText( item.stName )
		self.__pyStName.font = "songti.font"
		self.__pyStName.text = ""
		
		self.__pyStLevel = StaticText( item.stLevel )
		self.__pyStLevel.font = "songti.font"
		self.__pyStLevel.text = ""
		self.daofa = None
		
		self.__dropEvents = {}
		self.__dropEvents[DragMark.SERMON_COMMON_WND] = DropHandlers.fromTaoHeartCom
		self.__dropEvents[DragMark.SERMON_EQUIP_WND] = DropHandlers.fromTaoHeartEquip
	
	def __onMouseEnter( self, pyIcon ) :
		if self.pyBinder:
			self.pyBinder.onMouseEnter( self.dragMark )
		dsp = ""
		if self.daofa:
			quality = self.daofa.quality
			type = self.daofa.type
			level = self.daofa.level
			color = QAColor[quality]
			nameDsp = PL_Font.getSource( "%s %s"%( daofaDatas[quality][type]["name"], "Lv.%d"%level ), fc = color )
			exp = self.daofa.getLevelExp()
			expMax = self.daofa.getExpMax()
			expStr = ""
			if expMax == 0:
				expStr = "已满"
			else:
				expStr = "%d/%d"%( exp, expMax )
			expDsp = "道法经验 %s"%expStr
			skillDsp = ""
			if quality > ItemTypeEnum.CQT_WHITE:
				skillID = daofaDatas[quality][type]["levelData"][level]
				skill = skills.getSkill( skillID )
				if skill is not None:							#可以获取技能实例
					skillDsp = "   " + skill.getDescription()
				else:
					skillDsp = "%s %d"%( daofaDatas[quality][type]["describe"], skillID )
			infoDsp = PL_Font.getSource( "%s"%skillDsp, fc = ( 204, 51, 0, 255 ) )
			dsp = nameDsp + PL_NewLine.getSource() + expDsp + PL_NewLine.getSource() + infoDsp
		elif not self.pyBinder.actived and \
		self.daoxinID == csdefine.KB_EQUIP_DAO_XIN_ID:
			dsp = labelGather.getText( "SermonSys:TaoHeart", "unlock" )%( self.orderID*10 + 30 )
		if dsp != "":
			toolbox.infoTip.showToolTips( self, dsp )

	def __onMouseLeave( self, pyIcon ) :
		if self.pyBinder:
			self.pyBinder.onMouseLeave( self.dragMark )
		toolbox.infoTip.hide()
	
	def __onIconLClick( self, pyIcon ) :
		if self.daoxinID == csdefine.KB_COM_DAO_XIN_ID:
			if not self.pyBinder.actived:
				BigWorld.player().getActiveGridCost( self.orderID )
			
	def onDragStart_( self, pyDragged ) :
		Control.onDragStart_( self, pyDragged )
		return True
	
	def onDragStop_( self, pyDragged ) :
		Control.onDragStop_( self, pyDragged )
		daofa = pyDragged.daofa
		if daofa is None:return False
		daoxinID = daofa.daoXinID
		name = daofa.name
		if not ruisMgr.isMouseHitScreen() : return False
		pyBinder = pyDragged.pyBinder
		if pyBinder is None:return False
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().confirmRemoveDaofa( daofa.uid )
		showMessage( mbmsgs[0x10a5] % name, "", MB_OK_CANCEL, query, pyOwner = pyBinder.pyTopParent )
		return True
		
	def onDrop_( self, pyTarget, pyDropped ) :
		Control.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True

	def __onIconRClick( self, pyIcon ) :
		srcDaofa = self.daofa
		if srcDaofa is None:
			return
		if srcDaofa.isLocked:return
		player = BigWorld.player()
		srcDaoxinID = self.daoxinID
		srcUID = self.daofa.uid
		dstDaoxinID = 0
		if srcDaoxinID == csdefine.KB_COM_DAO_XIN_ID:
			dstDaoxinID = csdefine.KB_EQUIP_DAO_XIN_ID
		else:
			dstDaoxinID = csdefine.KB_COM_DAO_XIN_ID
		player.autoMoveDaofaTo( srcUID, dstDaoxinID )
		
	def update( self, daofa ):
		self.daofa = daofa
		if daofa:
			quality = daofa.quality
			type = daofa.type
			name = daofaDatas[quality][type]["name"]
			icon = "icons/%s.dds"%daofaDatas[quality][type]["icon"]
			color = QAColor[quality]
			self.__pyStName.text = name
			if quality > ItemTypeEnum.CQT_WHITE:
				self.__pyStName.color = color
			self.__pyStLevel.text = "Lv.%d"%daofa.level
			self.__pyStLevel.color = color
			self.__pyIcon.texture = "guis/general/sermonsys/sermonwnd/icons.dds"
			util.setGuiState( self.__pyIcon.gui, ( 3, 2 ), ItemQAColorMode[quality] )
			isLocked = daofa.isLocked
			self.lock( isLocked )
		else:
			self.__pyStName.text = ""
			self.__pyStLevel.text = ""
			self.__pyIcon.texture = ""

	def lock( self, isLocked ):
		"""
		锁定/解锁道法
		"""
		if isLocked:
			util.setGuiState( self.__pyIcon.gui, ( 3, 2 ), ( 3, 2 ) )
		else:
			util.setGuiState( self.__pyIcon.gui, ( 3, 2 ), ItemQAColorMode[self.daofa.quality] )
	
	def getLockInfo( self, locker ):
		"""
		获取锁定信息
		"""
		return self.daofa

class DropHandlers :
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def fromTaoHeartCom( pyTarget, pyDropped ):
		"""
		从道心普通包裹拖放进来
		"""
		srcDaofa = pyDropped.daofa
		if srcDaofa:
			srcUID = srcDaofa.uid
			pyBinder = pyTarget.pyBinder
			dstDaofa = pyTarget.daofa
			if dstDaofa and dstDaofa.uid == srcUID:
				return
			if pyBinder and not pyBinder.actived:
				showMessage( mbmsgs[0x10a3] , "", MB_OK, None )
				return
			dstDaoxinID = pyTarget.daoxinID
			dstOrder = pyTarget.orderID
			BigWorld.player().moveDaofaTo( srcUID, dstDaoxinID, dstOrder )
	
	@staticmethod
	def fromTaoHeartEquip( pyTarget, pyDropped ):
		"""
		从道心装备包裹拖放进来
		"""
		srcDaofa = pyDropped.daofa
		if srcDaofa:
			srcUID = srcDaofa.uid
			pyBinder = pyTarget.pyBinder
			dstDaofa = pyTarget.daofa
			if dstDaofa and dstDaofa.uid == srcUID:
				return
			if pyBinder and not pyBinder.actived:
				showMessage( mbmsgs[0x10a3] , "", MB_OK, None )
				return
			dstDaoxinID = pyTarget.daoxinID
			dstOrder = pyTarget.orderID
			BigWorld.player().moveDaofaTo( srcUID, dstDaoxinID, dstOrder )