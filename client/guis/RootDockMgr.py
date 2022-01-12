# -*- coding: gb18030 -*-
#
# $Id: RootDockMgr.py,v 1.4 2008-08-01 03:30:30 huangyongwei Exp $


"""
2008/5/27: WindowShowManager( writen by zhangyuxing )
2008/5/28: RootDockMgr( rewriten by huangyongwei )
"""

import sys
from AbstractTemplates import Singleton
from Weaker import WeakList
from bwdebug import *
from gbref import rds

class RootDockMgr( Singleton ) :
	__cc_start_pos = 20, 80

	def __init__( self ):
		self.__hookNames = []
		self.__initialize()
		self.__pyShowedRoots = WeakList()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		"""
		初始化所有要停靠的 UI 的 hookName
		"""
		self.__hookNames.append( "helpWindow" )
		self.__hookNames.append( "playProWindow" )
		self.__hookNames.append( "kitBag" )
		self.__hookNames.append( "skillList" )
		self.__hookNames.append( "skillTrainer" )
		self.__hookNames.append( "questHelp" )
		self.__hookNames.append( "tradeWindow" )
		self.__hookNames.append( "darkMerchantWindow" )
		self.__hookNames.append( "specialMerchantWindow" )
		self.__hookNames.append( "tradingWindow" )
		self.__hookNames.append( "talkingWindow" )
		self.__hookNames.append( "storeWindow" )
		self.__hookNames.append( "relationWindow" )
		self.__hookNames.append( "petWindow" )
		self.__hookNames.append( "mailWindow" )
		self.__hookNames.append( "equipProduce" )
		self.__hookNames.append( "shenShouBeckon" )

	# -------------------------------------------------
	def __layout( self ) :
		"""
		排列所有 UI 停靠的位置
		"""
		left, top = self.__cc_start_pos
		for idx in xrange( len( self.__pyShowedRoots ) ) :
			pyRoot = self.__pyShowedRoots[idx]
			if idx > 0 : left = self.__pyShowedRoots[idx - 1].right
			pyRoot.pos = left, top

	# -------------------------------------------------
	def __onRootShowed( self, pyRoot ) :
		"""
		当有一个窗口显示时被调用
		"""
		if pyRoot.hookName == "kitBag" :
			pyRoot.r_right = 1
			pyRoot.top = self.__cc_start_pos[1]
			return
		if len( self.__pyShowedRoots ) :
			pyRoot.left = self.__pyShowedRoots[-1].right
		if pyRoot not in self.__pyShowedRoots :
			self.__pyShowedRoots.append( pyRoot )
		self.__layout()

	def __onRootHided( self, pyRoot ) :
		"""
		当有一个窗口隐藏时被调用
		"""
		if pyRoot in self.__pyShowedRoots :
			self.__pyShowedRoots.remove( pyRoot )
		self.__layout()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		当角色进入世界时被调用
		"""
		while len( self.__hookNames ) :
			hookName = self.__hookNames.pop( 0 )
			try :
				pyRoot = getattr( rds.ruisMgr, hookName )
			except Exception, err :
				EXCEHOOK_MSG( "no root ui named '%s'!" % hookName )
			pyRoot.onBeforeShow.bind( self.__onRootShowed )
			pyRoot.onAfterClosed.bind( self.__onRootHided )

	def onRootShowed(self,pyRoot):
		self.__onRootShowed(pyRoot)

	def onRootHided(self,pyRoot):
		self.__onRootHided(pyRoot)



# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
rootDockMgr = RootDockMgr()
