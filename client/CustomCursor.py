# -*- coding: gb18030 -*-
# $Id: CursorMgr.py,v 1.8 2008-02-22 06:57:00 huangyongwei Exp $
#
"""
implement cursor manager

2008.09.12: writen by huangyongwei
"""

import GUI
import ResMgr
import csol
from bwdebug import *
from AbstractTemplates import Singleton

class CustomCursor( Singleton ) :
	def __init__( self ) :
		self.__mcursor = GUI.mcursor()
		self.__sect = ResMgr.openSection( "guis/otheruis/cursor/cursors.xml" )
		self.__locked = False						# 是否锁定鼠标，如果锁定鼠标，则在没解锁之前，所有设置都是无效的

		self.set( "normal" )						# 默认为普通鼠标


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def hotSpot( self ) :
		"""
		鼠标指针在鼠标贴图中的位置
		"""
		return self.__sect[self.shape].readVector2( "hotSpot" )

	@property
	def downSpot( self ) :
		"""
		像素坐标表示鼠标大小
		"""
		return self.__sect[self.shape].readVector2( "downSpot" )

	# ---------------------------------------
	@property
	def pos( self ) :
		"""
		鼠标在屏幕上的位置（像素坐标）
		"""
		return csol.pcursorPosition()

	@property
	def rpos( self ) :
		"""
		鼠标在屏幕上的位置(相对坐标)
		"""
		return csol.rcursorPosition()

	@property
	def dpos( self ) :
		"""
		鼠标右下角位置( 像素坐标 )
		"""
		x, y = self.pos
		dx, dy = self.downSpot
		hx, hy = self.hotSpot
		left = x + dx - hx
		bottom = y + dy - hy
		return left, bottom

	@property
	def rdpos( self ) :
		"""
		鼠标右下角位置( 相对坐标 )
		"""
		dx, dy = self.dpos
		rright = 2 * ( dx / BigWorld.screenWidth() ) - 1
		rbottom = 1 - 2 * ( dy / BigWorld.screenHeight() )

	# -------------------------------------------------
	@property
	def shape( self ) :
		"""
		当前鼠标名称
		"""
		name = self.__mcursor.shape
		if self.grayed : 						# 如果是灰色状态
			return name[2:]						# 则，去掉灰色状态前缀
		return name

	@property
	def grayed( self ) :
		"""
		是否处于灰色状态
		"""
		return self.__mcursor.shape.startswith( "g_" )

	@property
	def locked( self ) :
		"""
		是否处于锁定状态
		"""
		return self.__locked


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def set( self, name, isGray = False ) :
		"""
		设置鼠标
		@type			name   : str
		@param			name   : 鼠标名称
		@type			isGray : bool
		@param			isGray : 是否使用灰色状态
		@rype				   : str
		@return				   : 如果鼠标处于锁定状态，则返回 None，否则返回旧的鼠标名称
		"""
		assert self.__sect.has_key( name ), "error cursor name"
		if self.__locked : return None			# 鼠标被锁定，则返回 None 表示设置失败
		oleName = self.shape					# 记录下旧的鼠标名称
		self.__mcursor.shape = name				# 设置新鼠标
		if isGray : self.gray()					# 设置为灰色状态
		else : self.degray()					# 设置为非灰色状态
		return oleName							# 返回旧鼠标

	# -------------------------------------------------
	def lock( self, shape, isGray = False ) :
		"""
		锁定鼠标为某个形状
		注意：如果有另外一个形状锁住了鼠标，则这里会锁失败（必需解开前面一个形状的锁，才能锁定）
		@type		shape : str
		@param		shape : 要锁定的形状
		@rtype			  : bool
		@return			  : 返回设置前的锁定状态
		"""
		locked = self.__locked
		if locked : return locked
		self.set( shape, isGray )
		self.__locked = True
		return locked

	def unlock( self, shape, newShape = None ) :
		"""
		解锁鼠标
		@type		shape	 : str
		@param		shape	 : 要解锁的形状，如果当前不处于这种形状，则会解锁失败
		@type		newShape : str
		@param		newShape : 解锁后，回复的新形状
		@rtype				 : bool
		@return				 : 返回设置前的锁定状态
		"""
		locked = self.__locked
		if locked and shape != self.shape :
			return True
		self.__locked = False
		if newShape :
			self.set( newShape )
		return locked

	# -------------------------------------------------
	def gray( self ) :
		"""
		使鼠标变灰
		@rtype				 : bool
		@param				 : 改变成功的话返回 True，否则返回 False
		"""
		if self.__locked : return False			# 鼠标被锁定，则返回
		if self.grayed : return True			# 如果已经是灰色鼠标，则不用修改
		name = "g_%s" % self.shape				# 获取灰色鼠标名称
		if self.__sect.has_key( name ) :		# 如果存在灰色贴图
			self.__mcursor.shape = name			# 则，设置为灰色鼠标
			return True							# 并返回设置成功
		return False

	def degray( self ) :
		"""
		撤销灰色状态
		"""
		if self.__locked : return False			# 鼠标被锁定，则返回
		if not self.grayed : return True		# 已经处于非灰色状态
		self.set( self.shape )					# 重新设置即可
		return True

	# -------------------------------------------------
	def normal( self, isGray = False ) :
		"""
		设置鼠标为普通模式
		@type			isGray : bool
		@param			isGray : 是否使用灰色状态
		"""
		if self.__mcursor.shape == "normal" :
			return
		if self.__locked : return False			# 鼠标被锁定，则返回
		self.__mcursor.shape = "normal"
		if isGray : self.gray()
		return True
