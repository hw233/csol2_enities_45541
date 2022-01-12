# -*- coding: gb18030 -*-

# 该菜单在任何地方需要时都可以在鼠标处弹出，
# 菜单结构由调用者按照约定的规则自行定制。
# by ganjinxing 2010-11-03

import weakref
from bwdebug import *
from cscollections import Queue
from AbstractTemplates import Singleton
import event.EventCenter as ECenter

from guis.uidefine import MIStyle
from guis.controls.ContextMenu import ContextMenu, DefMenuItem


class GlobalMenu( Singleton ) :

	def __init__( self ) :
		self.__pyMenu = None
		self.__releaseWhenHide = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBeforePopup( self ) :
		"""
		为了菜单能弹出，这个函数需要返回True
		"""
		return True

	def __onMenuItemClicked( self, pyMuItem ) :
		"""
		菜单项点击触发
		"""
		try :
			pyMuItem.handler()
		except :
			EXCEHOOK_MSG()

	def __onHide( self ) :
		"""
		关闭菜单
		"""
		if self.__releaseWhenHide :
			self.__pyMenu = None
			self.__class__.releaseInst()

	def __popup( self, struct, pyOwner = None ) :
		"""
		弹出菜单
		"""
		if self.__construct( struct ) :
			self.__pyMenu.popup( pyOwner )
		else :
			self.__onHide()
			ERROR_MSG( "Build menu fail, please contact the relative person!" )

	def __construct( self, struct ) :
		"""
		根据给出的数据，创建菜单
		@param		struct : 菜单项结构
							(
							  ( muItemText1, handler1 ),					# 菜单项1，
							  ( muItemText2, (								# 菜单项2
							  		( subMuItemtext21, handler21 ),			# 菜单项2的子菜单，
							  		), ),
							  ( "SPLITTER", 1 )								# 创建1根分隔栏
							  ( muItemText3, (								# 菜单项3
							  		( subMuItemtext31, handler31 ),			# 菜单项3的子菜单1，
							  		( subMuItemtext32, (					# 菜单项3的子菜单2，
							  			( subMuItemtext321, handler321 ),	# 菜单项3的子菜单2的子菜单1，
							  			), ),
							  		), ),
							  ( muItemText4, handler4 ),					# 菜单项4
							)
							注意：每一个菜单项都是一个二元组
		@type		struct : tuple
		"""
		if self.__pyMenu :
			self.__releaseWhenHide = False
			self.__pyMenu.clear()
		else :
			self.__pyMenu = ContextMenu()
			self.__pyMenu.onItemClick.bind( self.__onMenuItemClicked )
			self.__pyMenu.onAfterClose.bind( self.__onHide )
			self.__pyMenu.onBeforePopup.bind( self.__onBeforePopup )
		self.__releaseWhenHide = True
		return self.__buildMuItems( struct )

	def __buildMuItems( self, struct ) :
		"""
		生成菜单项
		"""
		if self.__pyMenu is None : return False
		if len( struct ) == 0 : return False

		def buildMI( parent, label, style = MIStyle.COMMON ) :
			muItem = DefMenuItem( label, style )
			parent.add( muItem )
			return muItem

		muQueue = Queue()
		muQueue.enter( ( self.__pyMenu, struct ) )
		while muQueue.length() :
			muParent, muItems = muQueue.leave()
			for muLabel, muKernel in muItems :
				if type( muLabel ) is not str :
					ERROR_MSG( "Error struct of menu items:", \
						str( muLabel ), str( muKernel ) )
					return False
				elif muLabel == "SPLITTER" :									# 创建分隔栏
					if type( muKernel ) is int :
						for i in xrange( muKernel ) :
							buildMI( muParent, "", MIStyle.SPLITTER )
					else :
						ERROR_MSG( "Error struct of menu items:", \
							str( muLabel ), str( muKernel ) )
						return False
				elif callable( muKernel ) :										# 创建菜单项
					subMuItem = buildMI( muParent, muLabel )
					subMuItem.handler = muKernel
				elif type( muKernel ) is tuple :								# 子菜单入队列
					subMuItem = buildMI( muParent, muLabel )
					muQueue.enter( ( subMuItem.pySubItems, muKernel ) )
				else :
					ERROR_MSG( "Error struct of menu items:", \
						str( muLabel ), str( muKernel ) )
					return False
		return True


	# ----------------------------------------------------------------
	# class methods
	# ----------------------------------------------------------------
	@classmethod
	def registerEvents( SELF ) :
		ECenter.registerEvent( "EVT_ON_POPUP_GLOBAL_MENU", SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.inst.__popup( *args )


GlobalMenu.registerEvents()
