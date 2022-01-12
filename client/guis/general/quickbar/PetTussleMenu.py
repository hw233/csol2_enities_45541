# -*- coding: gb18030 -*-

# implement PetMenuItem
# by ganjinxing 2010-01-05


from guis import *
from guis.controls.ContextMenu import MenuItem
from guis.controls.ContextMenu import ContextMenu
from guis.controls.Button import Button
from LabelGather import labelGather
import csdefine


class PetMenuItem( MenuItem ) :

	_MENU_ITEM = None

	def __init__( self ) :
		if PetMenuItem._MENU_ITEM is None :
			PetMenuItem._MENU_ITEM = GUI.load( "guis/general/quickbar/petbar/pet_menu_item.gui" )
			uiFixer.firstLoadFix( PetMenuItem._MENU_ITEM )
		muItem = util.copyGuiTree( PetMenuItem._MENU_ITEM )
		MenuItem.__init__( self, item = muItem )

		self.backColors_[UIState.COMMON] = 255, 255, 255, 255
		self.backColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.backColors_[UIState.DISABLE] = 255, 255, 255, 255

		self.__pyBtn = Button( muItem.icon )
		self.__pyBtn.size = 32,32
		self.__pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtn.width = 33


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getRealWidth( self ) :
		"""
		获取菜单项的真实宽度
		"""
		return self.width


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getPyButton( self ) :
		return self.__pyBtn

	pyBtn = property( _getPyButton )



class PetTussleMenu :

	STATUS_MAP = {
			csdefine.PET_TUSSLE_MODE_ACTIVE: ( labelGather.getText( "quickbar:petMenu", "tipsActive" ),
												"guis/general/quickbar/petbar/activebtn.dds" ),
			csdefine.PET_TUSSLE_MODE_PASSIVE: ( labelGather.getText( "quickbar:petMenu", "tipsPassive" ),
												"guis/general/quickbar/petbar/passivebtn.dds" ),
			csdefine.PET_TUSSLE_MODE_GUARD: ( labelGather.getText( "quickbar:petMenu", "tipsDefense" ),
												"guis/general/quickbar/petbar/recoverybtn.dds" ),
			}

	def __init__( self, staticBtn ) :
		self.__pySTBtn = Button( staticBtn )
		self.__pySTBtn.size = 32, 32
		self.__pySTBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySTBtn.width = 33												# 为了使mapping正确设置，这里取巧了
		self.__pySTBtn.onLClick.bind( self.__popupMenu )
		self.__pySTBtn.onMouseEnter.bind( self.__showTip )
		self.__pySTBtn.onMouseLeave.bind( self.__hideTip )
		self.__pySTBtn.mode = None

		self.__pyTSMenu = None													# 弹出菜单


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __popupMenu( self ) :
		self.__pyTSMenu = ContextMenu()
		elements = self.__pyTSMenu.getGui().elements
		for elem in elements.values():
			elem.texture = ""
		self.__pyTSMenu.onBeforePopup.bind( self.__onBeforMUPopup )
		self.__pyTSMenu.onAfterClose.bind( self.__destroyMenu )
		currMode = self.__pySTBtn.mode
		for tussleMode, ( dsp, texture ) in self.STATUS_MAP.items() :
			if tussleMode != currMode :
				pyMenuItem = PetMenuItem()
				pyMenuBtn = pyMenuItem.pyBtn
				pyMenuBtn.mode = tussleMode
				pyMenuBtn.dsp = dsp
				pyMenuBtn.texture = texture
				pyMenuBtn.onLClick.bind( self.__changeTussleMode )
				pyMenuBtn.onMouseEnter.bind( self.__showTip )
				pyMenuBtn.onMouseLeave.bind( self.__hideTip )
				self.__pyTSMenu.add( pyMenuItem )
				pyMenuItem.left = 0
		self.__pyTSMenu.center = self.__pySTBtn.centerToScreen - 1
		self.__pyTSMenu.bottom = self.__pySTBtn.topToScreen
		self.__pyTSMenu.show()

	def __changeTussleMode( self, pyMenuBtn ) :
		expectMode = pyMenuBtn.mode
		BigWorld.player().pcg_setTussleMode( expectMode )
		self.__pyTSMenu.hide()

	def __onBeforMUPopup( self ) :
		"""
		为了调用ContextMenu的show时，菜单能显示出来，
		这个函数得返回True
		"""
		return True

	def __destroyMenu( self ) :
		self.__pyTSMenu = None
		PetMenuItem._MENU_ITEM = None

	def __showTip( self, pyBtn ) :
		"""
		显示提示消息
		"""
		toolbox.infoTip.showToolTips( pyBtn, pyBtn.dsp )

	def __hideTip( self ) :
		"""
		隐藏提示消息
		"""
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTussleMode( self, mode ) :
		oldMode = self.__pySTBtn.mode
		if oldMode is not None and mode == oldMode : return
		if self.__pyTSMenu is not None :
			for pyMenuItem in self.__pyTSMenu :
				pyMenuBtn = pyMenuItem.pyBtn
				if pyMenuBtn.mode == mode :
					dsp, texture = self.STATUS_MAP[ oldMode ]
					pyMenuBtn.mode = oldMode
					pyMenuBtn.dsp = dsp
					pyMenuBtn.texture = texture
					break
		dsp, texture = self.STATUS_MAP[ mode ]
		self.__pySTBtn.mode = mode
		self.__pySTBtn.dsp = dsp
		self.__pySTBtn.texture = texture

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getPySTButton( self ) :
		return self.__pySTBtn

	pySTBtn = property( _getPySTButton )
