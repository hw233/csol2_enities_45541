# -*- coding: gb18030 -*-

# implement shortcut setting panel
# written by ganjinxing 2009-10-5


from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListPanel import ListPanel
from KeySetter import KeySetter
from LabelGather import labelGather
import event.EventCenter as ECenter


# --------------------------------------------------------------------
# 快捷键面板的基类，不可直接实例化
# --------------------------------------------------------------------
class ShortcutPanel( TabPanel ):
	def __init__( self, panel, pyBinder ):
		TabPanel.__init__( self, panel, pyBinder )
		self.pyLPSetters_ = None
		self.initialize_( panel )
		
		self.changed = False

	def hide(self):
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onShow( self ) :
		"""
		版面显示被调用
		"""
		pass

	def onHide( self ) :
		"""
		版面隐藏时被调用
		"""
		self.pyLPSetters_.pySelItem = None

	# -------------------------------------------------
	def setDefault( self ) :
		"""
		将各选项恢复默认设置
		"""
		for pySetter in self.pyLPSetters_.pyItems :
			pySetter.setToDefault()
		self.onOK()
		self.changed = False
		ECenter.fireEvent( "EVT_ON_SHORTCUT_CHANGED", False )

	def onApplied( self ) :
		self.onOK()

	def onOK( self ) :
		if self.pyLPSetters_.pySelItem:
			self.pyLPSetters_.pySelItem.tabStop = False
		self.pyLPSetters_.pySelItem = None
		self.changed = False
		ECenter.fireEvent( "EVT_ON_SHORTCUT_CHANGED", False )
		return True

	def onCancel( self ) :
		self.pyLPSetters_.pySelItem = None

	def onEnterWorld( self ) :
		pass

	def onActivated( self ) :
		"""
		所属窗口激活时被调用
		"""
		pySelItem = self.pyLPSetters_.pySelItem
		if pySelItem :
			pySelItem.tabStop = True

	def onInactivated( self ) :
		"""
		所属窗口取消激活状态时被调用
		"""
		pySelItem = self.pyLPSetters_.pySelItem
		if pySelItem :
			pySelItem.tabStop = False
			
	def onKeyChanged( self, changed ):
		self.changed = changed

# --------------------------------------------------------------------
# 行为快捷键设置面板
# --------------------------------------------------------------------
class SCActionPanel( ShortcutPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/scAction.gui" )
		uiFixer.firstLoadFix( panel )
		ShortcutPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ) :
		self.pyLPSetters_ = ShortcutSect( panel.clipPanel, panel.sbar, self )
		self.pyLPSetters_.resetSetters( labelGather.getText( "gamesetting:scAct", "groupText" ), 30 )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.bgTitle.stTitle, "gamesetting:scAct", "stTitle" )


# --------------------------------------------------------------------
# 界面快捷键设置面板
# --------------------------------------------------------------------
class SCDisplayPanel( ShortcutPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/scDisplay.gui" )
		uiFixer.firstLoadFix( panel )
		ShortcutPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ) :
		self.pyLPSetters_ = ShortcutSect( panel.clipPanel, panel.sbar, self )
		self.pyLPSetters_.resetSetters( labelGather.getText( "gamesetting:scDsp", "groupText" ), 24 )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.bgTitle.stTitle, "gamesetting:scDsp", "stTitle" )


# --------------------------------------------------------------------
# 快捷栏设置面板
# --------------------------------------------------------------------
class SCQuickBarPanel( ShortcutPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/scQuickBar.gui" )
		uiFixer.firstLoadFix( panel )
		ShortcutPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ) :
		self.pyLPSetters_ = ShortcutSect( panel.clipPanel, panel.sbar, self )
		self.pyLPSetters_.resetSetters( labelGather.getText( "gamesetting:scQB", "groupText" ), 26 )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.bgTitle.stTitle, "gamesetting:scQB", "stTitle" )


# --------------------------------------------------------------------
# 战斗快捷键设置
# --------------------------------------------------------------------
class SCCombatPanel( ShortcutPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/scCombat.gui" )
		uiFixer.firstLoadFix( panel )
		ShortcutPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ) :
		self.pyLPSetters_ = CombatSCSect( panel,self )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.pnl_petCmt.bgTitle.stTitle, "gamesetting:scCmt", "stPetTitle" )
		labelGather.setLabel( panel.pnl_roleCmt.bgTitle.stTitle, "gamesetting:scCmt", "stRoleTitle" )


# -----------------------------------------------------
# 战斗面板由角色战斗和宠物战斗两个面板组成
# -----------------------------------------------------
class CombatSCSect( object ) :

	def __init__( self, panel, pyBinder = None ) :
		self.__pyRoleSetters = ShortcutSect( panel.pnl_roleCmt.clipPanel, panel.pnl_roleCmt.sbar, pyBinder )
		self.__pyRoleSetters.resetSetters( labelGather.getText( "gamesetting:scCmt", "groupTextRole" ), 24 )
		self.__pyRoleSetters.bindSelectedEvent( self.__onRoleSetterSelected, True )

		self.__pyPetSetters = ShortcutSect( panel.pnl_petCmt.clipPanel, panel.pnl_petCmt.sbar, pyBinder )
		self.__pyPetSetters.resetSetters( labelGather.getText( "gamesetting:scCmt", "groupTextPet" ), 24 )
		self.__pyPetSetters.bindSelectedEvent( self.__onPetSetterSelected, True )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onRoleSetterSelected( self, pySetter ) :
		"""
		这里控制同时只能选择一个面板中的子键
		"""
		if pySetter is not None :
			self.__pyPetSetters.pySelItem = None

	def __onPetSetterSelected( self, pySetter ) :
		"""
		这里控制同时只能选择一个面板中的子键
		"""
		if pySetter is not None :
			self.__pyRoleSetters.pySelItem = None


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def pyItems( self ) :
		pySTItems = self.__pyRoleSetters.pyItems
		pySTItems.extend( self.__pyPetSetters.pyItems )
		return pySTItems

	def _getSelItem( self ) :
		roleSelItem = self.__pyRoleSetters.pySelItem
		if roleSelItem is not None :
			return roleSelItem
		return self.__pyPetSetters.pySelItem

	def _setSelItem( self, pyItem ) :
		if pyItem is None :
			self.__pyPetSetters.pySelItem = pyItem
			self.__pyRoleSetters.pySelItem = pyItem
		elif pyItem in self.__pyPetSetters.pyItems :
			self.__pyPetSetters.pySelItem = pyItem
		else :
			self.__pyRoleSetters.pySelItem = pyItem

	pySelItem = property( _getSelItem, _setSelItem )


# --------------------------------------------------------------------
# 快捷键设置面板
# --------------------------------------------------------------------
class ShortcutSect( object ) :

	def __init__( self, panel, scrollBar, pyBinder = None ) :
		self.__pyLPSetters = ListPanel( panel, scrollBar )
		self.__pyLPSetters.autoSelect = False
		self.__pyLPSetters.sbarState = ScrollBarST.AUTO
		self.__pyLPSetters.onItemSelectChanged.bind( self.onSetterSelectChanged_ )
		self.pyBinder = pyBinder


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSetterSelectChanged_( self, pySetter ) :
		"""
		某个快捷键设置选项选中时被调用
		"""
		if pySetter : pySetter.tabStop = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetSetters( self, tag, itemHeight ) :
		"""
		重设快捷键按钮
		"""
		classifySCs = rds.shortcutMgr.getClassifyShortcuts()
		scInfos = classifySCs.get( tag, None )
		if scInfos is None :
			ERROR_MSG( "Can't find shortcut classify by tag %s!" % tag )
			return
		self.__pyLPSetters.clearItems()
		for scInfo in scInfos :
			pySetter = KeySetter( scInfo, self.pyBinder )
			pySetter.height = itemHeight
			pySetter.left =10
			self.__pyLPSetters.addItem( pySetter )

	def bindSelectedEvent( self, method, add = False ) :
		"""
		允许另绑定类外其他实例的方法
		"""
		self.__pyLPSetters.onItemSelectChanged.bind( method, add )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def pyItems( self ) :
		return self.__pyLPSetters.pyItems

	def _getSelItem( self ) :
		return self.__pyLPSetters.pySelItem

	def _setSelItem( self, pyItem ) :
		self.__pyLPSetters.pySelItem = pyItem

	pySelItem = property( _getSelItem, _setSelItem )

