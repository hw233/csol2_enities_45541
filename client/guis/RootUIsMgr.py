# -*- coding: gb18030 -*-
#
# $Id: RootUIsMgr.py,v 1.25 2008-08-26 02:12:22 huangyongwei Exp $

"""
the manager of roots' gui.

2005/10/20 : wirten by huangyongwei( RootUIsMgr )
2008/01/15 : rewirten by huangyongwei
"""

import weakref
import GUI
import Define
from cscollections import Stack
from cscollections import MapList
from Weaker import WeakList
from AbstractTemplates import Singleton
from bwdebug import *
from gbref import rds
from ShortcutMgr import shortcutMgr
from guis.UIFixer import uiFixer
from uidefine import ZSegs
from RootDockMgr import rootDockMgr
from UISounder import uiSounder

class RootUIsMgr( Singleton ) :
	"""
	顶层窗口管理器
	注意：添加到管理器中的 UI 采用弱引用，要持久保存窗口，请自行保存
	"""
	def __init__( self ) :
		self.__segRngs = {}											# UI 层叠分段：（起始深度，结束深度，激活时的深度）
		self.__segRngs[ZSegs.L1] = ( 0.11, 0.19, 0.1 )				# 第一层：最上层，一般用于设置 tooltip 这样的控件
		self.__segRngs[ZSegs.L2] = ( 0.21, 0.29, 0.2 )				# 第二层：一般用于菜单这样的控件
		self.__segRngs[ZSegs.L3] = ( 0.31, 0.39, 0.3 )				# 第三层：一般用于 always on top 这样的窗口
		self.__segRngs[ZSegs.L4] = ( 0.41, 0.49, 0.4 )				# 第四层：普通窗口
		self.__segRngs[ZSegs.L5] = ( 0.51, 0.59, 0.5 )				# 第五层：一般用于一直处于最下层的 UI

		self.__pyRoots = {}											# 保存所有的顶层窗口
		self.__pyRoots[ZSegs.L1] = WeakList()						# 保存第一次
		self.__pyRoots[ZSegs.L2] = WeakList()						# 保存第二层
		self.__pyRoots[ZSegs.L3] = WeakList()						# 保存第三层
		self.__pyRoots[ZSegs.L4] = WeakList()						# 保存第四层
		self.__pyRoots[ZSegs.L5] = WeakList()						# 保存第五层

		self.__pyVSRoots = MapList()								# 保存所有可见的 UI
		self.__pyVSRoots[ZSegs.L1] = WeakList()						# 保存第一层可见的窗口
		self.__pyVSRoots[ZSegs.L2] = WeakList()						# 保存第二层可见的窗口
		self.__pyVSRoots[ZSegs.L3] = WeakList()						# 保存第三层可见的窗口
		self.__pyVSRoots[ZSegs.L4] = WeakList()						# 保存第四层可见的窗口
		self.__pyVSRoots[ZSegs.L5] = WeakList()						# 保存第五层可见的窗口

		self.__pyActRoot = None										# 保存当前激活的窗口

		shortcutMgr.setHandler( "FIXED_ORDER_HIDE_WINDOW", self.__orderHideRoots )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __getSubDialogs( pyParent, pyRoot ) :
		"""
		获取指定窗口的所有子窗口
		注意：这种父子关系不是引擎 UI 的那种父子关系，而是 python UI 顶层窗口的父子关系
		返回每个层次窗口的顺序是：字窗口 --> 父窗口
		"""
		pyDialogs = {}
		pyTraveleds = []														# 临时保存已经遍历的窗口
		stack = Stack()															# 创建一个临时栈
		stack.push( pyParent )													# 指定窗口入栈
		while stack.size() > 0 :
			pyTop = stack.top()													# 获取栈顶窗口
			pySubDialogs = pyTop.pySubDialogs
			if pyTop not in pyTraveleds and len( pySubDialogs ) > 0 :			# 如果栈顶的窗口还没遍历过
				pyTraveleds.append( pyTop )										# 则添加到 已经遍历链表 中
				pySubDialogs.sort( key = lambda d : d.posZ, reverse = True )	# 按 Z 轴坐标顺序重新排列所有同层窗口
				if pyRoot in pySubDialogs :
					pySubDialogs.remove( pyRoot )
					pySubDialogs.append( pyRoot )								# 将指定的窗口放到最前面
				for pyDlg in pySubDialogs :										# 循环遍历 指定窗口 或 某子窗口 的子窗口
					zseg = pyDlg.posZSegment
					if zseg not in pyDialogs or pyDlg not in pyDialogs[zseg] : 	# 如果该子窗口不在子窗口列表中
						stack.push( pyDlg )										# 则入栈
			elif pyTop != pyParent and pyTop.rvisible :							# 如果栈顶的窗口已经遍历过，并且不是最底层的窗口
				pyDialog = stack.pop()
				zseg = pyDialog.posZSegment
				pyLayerDlgs = pyDialogs.get( zseg, None )
				if pyLayerDlgs :
					pyLayerDlgs.append( pyDialog )								# 则将该窗口出栈并添加到子窗口列表中
				else :
					pyDialogs[zseg] = [pyDialog]
			else :																# 否则
				stack.pop()														# 出栈
		return pyDialogs														# 返回各层次子窗口列表

	def __getRootDialogsTree( self, pyRoot ) :
		"""
		获取指定窗口的所有父窗口和子窗口列表
		链表的顺序是：字窗口 --> 父窗口
		"""
		pyOwner = pyRoot														# 我的父窗口
		while True :															# 一直向祖先
			if pyOwner.pyOwner is None :										# 追溯我的最上层父窗口
				break
			pyOwner = pyOwner.pyOwner
		pyDialogs = self.__getSubDialogs( pyOwner, pyRoot )
		zseg = pyOwner.posZSegment
		if zseg in pyDialogs :
			pyDialogs[zseg].append( pyOwner )
		else :
			pyDialogs[zseg] = [pyOwner]
		return pyDialogs														# 返回所有层次父子窗口列表

	# -------------------------------------------------
	def __addVSRoot( self, pyRoot ) :
		"""
		添加一个可见窗口到可见窗口列表
		"""
		zseg = pyRoot.posZSegment
		if pyRoot not in self.__pyVSRoots[zseg] :
			self.__pyVSRoots[zseg].append( pyRoot )

	def __removeVSRoot( self, pyRoot ) :
		"""
		从可见窗口列表中删除一个窗口
		"""
		zseg = pyRoot.posZSegment
		if pyRoot in self.__pyVSRoots[zseg] :
			self.__pyVSRoots[zseg].remove( pyRoot )

	# -------------------------------------------------
	def __activeTopRoot( self ) :
		"""
		激活最顶层的窗口
		"""
		pyRoots = self.getVSRoots()					# 获取所有可见窗口
		pyRoot = None
		for pyTmp in pyRoots :						# 顺序
			if pyTmp.activable :					# 找出第一个
				pyRoot = pyTmp						# 可被激活的窗口
		if pyRoot is not None :						# 如果找到
			self.activeRoot( pyRoot, False )		# 则激活之

	# -------------------------------------------------
	def __orderHideRoots( self ) :
		"""
		顺序隐藏当前打开的窗口
		"""
		for pyRoot in self.getVSRoots() :			# 遍历所有可见窗口
			if pyRoot.escHide :						# 如果窗口允许按 esc 键隐藏
				pyRoot.hide()						# 则隐藏窗口
				return True							# 返回隐藏成功
		return False								# 返回隐藏不成功


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		游戏状态改变前被调用
		"""
		pyRoots = self.getRoots()
		for pyRoot in pyRoots :
			pyRoot.beforeStatusChanged( oldStatus, newStatus )			# 让状态改变通知所有窗口

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		游戏状态改变后被调用
		"""
		pyRoots = self.getRoots()
		for pyRoot in pyRoots :
			pyRoot.afterStatusChanged( oldStatus, newStatus )			# 让状态改变通知所有窗口

	def onRoleEnterWorld( self ) :
		"""
		当角色进入世界时被调用
		"""
		rootDockMgr.onRoleEnterWorld()									# 通知窗口停靠管理器

	def onRoleLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		"""
		for pyRoot in self.getRoots() :
			try :
				pyRoot.onLeaveWorld()									# 通知所有窗口角色已离开世界
			except Exception, err :
				EXCEHOOK_MSG( err )
		from guis.ScreenViewer import ScreenViewer
		ScreenViewer().onLeaveWorld()

	def onRoleInitialized( self ) :
		"""
		当角色初始化完毕时被调用
		"""
		for pyRoot in self.getRoots() :
			pyRoot.onEnterWorld()										# 通知所有窗口角色初始化完毕
		from guis.ScreenViewer import ScreenViewer
		ScreenViewer().onEnterWorld()

	# ---------------------------------------
	def onRootShow( self, pyRoot ) :
		"""
		当有一个窗口显示时被调用
		"""
		uiSounder.initRootSound( pyRoot )
		self.__addVSRoot( pyRoot )
		self.upgradeRoot( pyRoot )
		if pyRoot.activable :
			self.activeRoot( pyRoot, False )

	def onRootHide( self, pyRoot ) :
		"""
		当有一个窗口隐藏时被调用
		"""
		self.__removeVSRoot( pyRoot )
		if pyRoot == self.getActRoot() :
			self.__activeTopRoot()

	def onZSegmentChanged( self, pyRoot, oldSeg, newSeg ) :
		"""
		更改窗口深度
		"""
		pyRoots = self.__pyRoots[oldSeg]
		if pyRoot in pyRoots :
			pyRoots.remove( pyRoot )
			self.__pyRoots[newSeg].append( pyRoot )
		pyRoots = self.__pyVSRoots[oldSeg]
		if pyRoot in pyRoots :
			pyRoots.remove( pyRoot )
			self.__pyVSRoots[newSeg].append( pyRoot )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def add( self, pyRoot, hookName = "" ) :
		"""
		添加一个顶层窗口到管理器
		"""
		if hookName != "" :
			pyRoot.hookName = hookName
			uiSounder.onRootAdded( pyRoot )

		pyRoot.posZ = self.__segRngs[pyRoot.posZSegment][1]
		pyRoots = self.__pyRoots[pyRoot.posZSegment]
		if pyRoot not in pyRoots :
			GUI.addRoot( pyRoot.getGui() )
			pyRoots.append( pyRoot )
			uiFixer.firstDockRoot( pyRoot )
		if pyRoot.rvisible :
			self.__addVSRoot( pyRoot )

	def remove( self, pyRoot ) :
		"""
		从管理器中删除一个窗口
		"""
		zseg = pyRoot.posZSegment
		if pyRoot in self.__pyRoots[zseg] :
			self.__pyRoots[zseg].remove( pyRoot )
		self.__removeVSRoot( pyRoot )
		if pyRoot == self.getActRoot() :
			self.__activeTopRoot()

	# -------------------------------------------------
	def getRoots( self ) :
		"""
		获取管理器中的所有窗口
		"""
		pyRoots = []
		for rs in self.__pyRoots.itervalues() :
			pyRoots += rs.list()
		return pyRoots

	def getVSRoots( self ) :
		"""
		获取管理器中所有可见的窗口
		"""
		pyVSRoots = []
		for pyRoots in self.__pyVSRoots.values() :
			pyVSRoots += sorted( pyRoots.list(), key = lambda r : r.posZ )
		return pyVSRoots

	def getActRoot( self ) :
		"""
		获取当前被激活的窗口
		"""
		if self.__pyActRoot is None :
			return None
		return self.__pyActRoot()

	def getHitRoot( self, pos ) :
		"""
		获取指定点下的最上层那个 UI
		"""
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.getGui().hitTest( *pos ) :
				return pyRoot
		return None

	def getHitRoots( self, pos ) :
		"""
		获取被指定点击中的所有可见 UI
		"""
		pyRoots = []
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.getGui().hitTest( *pos ) :
				pyRoots.append( pyRoot )
		return pyRoots

	def getMouseHitRoot( self ) :
		"""
		获取当前被鼠标击中的最上面那个窗口
		"""
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.isMouseHit() : return pyRoot
		return None

	def getMouseHitRoots( self ) :
		"""
		获取鼠标击中的所有可见 UI
		"""
		pyRoots = []
		for pyRoot in self.getVSRoots():
			if not pyRoot.hitable : continue
			if pyRoot.isMouseHit() : pyRoots.append( pyRoot )
		return pyRoots

	# ---------------------------------------
	def isActRoot( self, pyRoot ) :
		"""
		判断指定窗口是否是激活窗口
		"""
		return pyRoot == self.getActRoot()

	def isMouseHitScreen( self ) :
		"""
		判断鼠标是否没有击中任何窗口
		"""
		return self.getMouseHitRoot() is None

	# -------------------------------------------------
	def activeRoot( self, pyRoot, upgrade = True ) :
		"""
		激活一个窗口，如果激活成功则返回 True，否则返回 False
		"""
		if not pyRoot.visible : return False
		if pyRoot not in self.getRoots() : return False
		if not pyRoot.activable : return False
		if upgrade :
			self.upgradeRoot( pyRoot )
		if pyRoot == self.getActRoot() :
			return True
		self.inactiveRoot()
		self.__pyActRoot = weakref.ref( pyRoot )
		pyRoot.onActivated()
		return True

	def inactiveRoot( self, pyRoot = None ) :
		"""
		取消一个窗口的激活状态，
		如果 pyRoot 为 None，则取消当前激活窗口的激活状态，并返回 True
		如果 pyRoot 不为 None，则判断当前激活的窗口是否是指定的窗口，如果不是，则返回 False，否则取消它的激活状态并返回 True
		"""
		pyActRoot = self.getActRoot()
		if pyActRoot is None : return False
		if pyRoot is None or pyRoot == pyActRoot :
			pyActRoot.onInactivated()
			self.__pyActRoot = None
			rds.uiHandlerMgr.onRootInactivated( pyActRoot )
			return True
		return False

	def upgradeRoot( self, pyRoot ) :
		"""
		将一个窗口提到前面显示
		"""
		def relayout( pyRoots, start, end ) :
			count = len( pyRoots )
			if count == 0 : return
			delta = ( end - start ) / count
			for i, pyTmp in enumerate( pyRoots ) :
				pyTmp.posZ = start + i * delta

		pyRDialogs = self.__getRootDialogsTree( pyRoot )	# 获取窗口的父子关系窗口树
		for zseg, pyDialogs in pyRDialogs.iteritems() :			# 重设各层可见 UI 的深度值
			start, end, act = self.__segRngs[zseg]
			pyVSRoots = self.__pyVSRoots[zseg].list()
			pyVSRoots.sort( key = lambda py : py.posZ )
			relayout( pyVSRoots, start, end )				# 重新排列同层的可见窗口的层次关系
			relayout( pyDialogs, act, start )				# 重新排列需要靠前显示的窗口关系列表
		GUI.reSort()
		GUI.reSortFocusList( pyRoot.getGui() )

	def upgradeMouseHitRoot( self ) :
		"""
		将当前鼠标击中的窗口提到前面显示
		"""
		pyRoot = self.getMouseHitRoot()
		if pyRoot is None : return False
		self.upgradeRoot( pyRoot )
		if pyRoot.activable :
			self.activeRoot( pyRoot, False )
		return True
		
	def addToVisibleRoot( self, pyRoot ):
		self.__addVSRoot( pyRoot )



# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
ruisMgr = RootUIsMgr()
