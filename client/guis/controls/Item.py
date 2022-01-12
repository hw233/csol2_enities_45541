# -*- coding: gb18030 -*-
#
# $Id: Item.py,v 1.27 2008-08-25 09:03:53 huangyongwei Exp $

"""
implement object/skill/quick base item class

2006.05.09: writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from guis.controls.Control import Control

class Item( Control ) :
	"""
	物品、技能、buff 等格子的基类
	"""
	def __init__( self, item = None, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		self.__index = 0							# Item 在父列表中的索引
		self.__selectable = False					# Item 是否可以被选中
		self.__selected = False						# Item 是否处于选中状态
		self.__description = ""						# Item 的描述信息
		self.__initialize( item )					# 初始化 Item

		self.__locked = False						# Item 是否处于锁定状态
		self.__itemInfo = None						# Item 对应的底层信息
		self.__mouseHighlight = True				# 鼠标进入时，是否高亮显示 item
		self.__isLocked = False						# Item 是否被改变颜色

	def subclass( self, item, pyBinder = None ) :
		Control.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def dispose( self ) :
		self.__itemInfo = None
		Control.dispose( self )

	def __del__( self ) :
		if Debug.output_del_Item :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Control.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# Item 被选中时触发

	@property
	def onSelectChanged( self ) :
		"""
		Item 被选中时触发
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.focus = False
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		Item.clear( self )

	# -------------------------------------------------
	def __select( self ) :
		"""
		选中 Item
		"""
		if self.selected : return
		self.__selected = True
		self.setState( UIState.SELECTED )
		self.onSelectChanged( True )

	def __deselect( self ) :
		"""
		取消选中
		"""
		if not self.selected : return
		self.__selected = False
		self.setState( UIState.COMMON )
		self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		"""
		当鼠标进入时被调用，在这里显示描述
		"""
		#self.update( self.itemInfo ) # 每次显示描述的时候都更新一下，保证描述是最新的——这样做是错的，因为有可能覆盖掉外部的修改。
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		toolbox.infoTip.showItemTips( self, dsp )

	def onDescriptionHide_( self ) :
		"""
		当鼠标离开时被调用，这这里因此描述
		"""
		toolbox.infoTip.hide( self )

	# -------------------------------------------------
	def onStateChanged_( self, state ) :
		pass

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		self.onDescriptionHide_()
		return True

	def onRMouseDown_( self, mods ) :
		Control.onRMouseDown_( self, mods )
		self.onDescriptionHide_()
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		if self.__mouseHighlight :
			toolbox.itemCover.highlightItem( self )
		if not BigWorld.isKeyDown( KEY_MOUSE0 ) :
			self.onDescriptionShow_()
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		self.setState( UIState.COMMON )
		toolbox.itemCover.normalizeItem()
		self.onDescriptionHide_()
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if self.itemInfo is None :
			return True
		return Control.onDragStart_( self, pyDragged )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		"""
		通过底层的 itemInfo 更新 Item 信息
		"""
		self.__itemInfo = itemInfo
		if itemInfo is None :
			self.onDescriptionHide_()
			self.clear()
		else :
			self.icon = itemInfo.icon
			self.description = itemInfo.description

	# ---------------------------------------
	def lock( self ) :
		"""
		锁定物品/技能格子
		"""
		self.__isLocked = True
		#self.focus = False
		#self.crossFocus = False
		self.dragFocus = False
		self.dropFocus = False

	def unlock( self ) :
		"""
		解锁格子
		"""
		self.__isLocked = False
		#self.focus = True
		#self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True

	def _getLock( self ) :
		"""
		获取格子颜色是否被改变
		"""
		return self.__isLocked

	def clear( self ) :
		"""
		清空 Item 信息
		"""
		self.__itemInfo = None
		self.icon = ( "", None )
		self.description = ""
		if self.__selectable :
			self.selected = False

	# -------------------------------------------------
	def setState( self, state ) :
		"""
		设置 Item 的状态
		"""
		if state == UIState.COMMON and self.selected :
			self.onStateChanged_( UIState.SELECTED )
		else :
			self.onStateChanged_( UIState.COMMON )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getLocked( self ) :
		return self.__locked

	def _setLocked( self, locked ) :
		if locked :
			self.setState( UIState.LOCKED )
		elif self.selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.COMMON )
		self.__locked = locked

	# ---------------------------------------
	def _getItemInfo( self ) :
		return self.__itemInfo

	# ---------------------------------------
	def _getMouseHighlight( self ) :
		return self.__mouseHighlight

	def _setMouseHighlight( self, highlight ) :
		self.__mouseHighlight = highlight

	# -------------------------------------------------
	def _setTexture( self, texture ) :
		Control._setTexture( self, texture )
		if texture.strip() != "" and self.texture == "" :
			self.getGui().textureName = "icons/tb_yw_sj_005.dds"
			self.mapping = ( ( 0, 0 ), ( 0, 1 ), ( 1, 1 ), ( 1, 0 ) )

	# -------------------------------------------------
	def _getIndex( self ) :
		return self.__index

	def _setIndex( self, index ) :
		self.__index = index

	# -------------------------------------------------
	def _getGBIndex( self ) :
		return self.__index

	# -------------------------------------------------
	def _getIcon( self ) :
		return ( self.texture, self.mapping )

	def _setIcon( self, icon ) :
		if isDebuged :
			assert isinstance( icon, ( tuple, str ) )
		isTuple = type( icon ) is tuple
		self.texture = ( isTuple and [icon[0]] or [icon] )[0]
		if not isTuple or icon[1] is None :
			self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )
		else :
			self.mapping = icon[1]

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, value ) :
		self.__selectable = value

	# -------------------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, selected ) :
		if not self.__selectable : return
		if selected == self.__selected : return
		if selected : self.__select()
		else : self.__deselect()

	# -------------------------------------------------
	def _getDescription( self ) :
		return self.__description

	def _setDescription( self, dsp ) :
		self.__description = dsp


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	isLocked = property( _getLock )										# 仅用于获取物品是否被改变颜色的信息
	locked = property( _getLocked, _setLocked )							# 设置 Item 的锁定状态
	itemInfo = property( _getItemInfo )									# 获取对应的底层 Item 信息
	mouseHighlight = property( _getMouseHighlight, _setMouseHighlight )	# 获取/设置鼠标进入 Item 时，是否高亮显示
	texture = property( Control._getTexture, _setTexture )				# 获取 Item 的贴图
	index = property( _getIndex, _setIndex )							# 获取/设置 Item 在父列表中的索引值
	gbIndex = property( _getGBIndex )									# 获取 Item 在所有父列表中的索引值
	icon = property( _getIcon, _setIcon )								# 获取/设置 Item 的图标：( texture, mapping )
	selectable = property( _getSelectable, _setSelectable )				# 设置 Item 是否可以被选中
	selected = property( _getSelected, _setSelected )					# 设置 Item 是否处于选中状态
	description = property( _getDescription, _setDescription )			# 获取/设置 Item 的描述信息
