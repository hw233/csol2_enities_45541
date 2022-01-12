# -*- coding: gb18030 -*-
#
# written by ganjinxing 2010-05-24
#
# 互斥窗口管理器，互斥的窗口添加到一个独立的分组。例如：
# 窗口A,B,C,D之间是互斥的，则在创建窗口实例时调用
# addMutexRoot 或者 addRootToMutexGroups 接口将实例添加
# 到管理器中即可。若想将窗口从互斥组移去，则应调用
# removeMutexPyGui 接口。
# 注意：目前仅支持继承至RootGUI的窗口之间的互斥。
# 示例如下：
#
# class A :
#	def __init__( self ) :
#		...
#		rds.mutexShowMgr.addMutexRoot( self, "mutexGroup0" )
#		...

# class B :
#	def __init__( self ) :
#		...
#		rds.mutexShowMgr.addMutexRoot( self, "mutexGroup0" )
#		...
#
# C、D实现也如上，这样A、B、C、D就被添加到了一个相同的互斥分组中
# 其中任何一个显示都会触发隐藏其他三个窗口的操作。


from Weaker import WeakSet
from AbstractTemplates import Singleton


class MutexShowMgr( Singleton ) :

	def __init__( self ) :
		self.__mutexGroups = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addMutexRoot( self, pyRoot, groupID ) :
		"""
		添加一个RootUI到管理器
		@param		pyRoot	: 脚本层UI实例
		@param		groupID	: 互斥组标识
		@type		groupID	: int or str
		"""
		mutexGroup = self.__mutexGroups.get( groupID )
		if mutexGroup is not None :
			mutexGroup.add( pyRoot )
		else :
			mutexGroup = WeakSet()
			mutexGroup.add( pyRoot )
			self.__mutexGroups[ groupID ] = mutexGroup
		if hasattr( pyRoot, "mtxMgr_mutexGroups" ) :
			pyRoot.mtxMgr_mutexGroups.add( groupID )
		else :
			pyRoot.mtxMgr_mutexGroups = set( [ groupID, ] )
			pyRoot.onBeforeShow.bind( self.__onBeforeRootShow )				# 绑定窗口显示事件

	def addRootToMutexGroups( self, pyRoot, groupList ) :
		"""
		@param		pyRoot	: 脚本层UI实例
		@param		groupID	: 互斥组标识
		@type		groupID	: list of int or str
		"""
		for groupID in groupList :
			self.addMutexRoot( pyRoot, groupID )

	def removeMutexRoot( self, pyRoot, groupID ) :
		"""
		@param		pyRoot	: 脚本层UI实例
		@param		groupID	: 互斥组标识
		@type		groupID	: int or str
		"""
		mutexGroup = self.__mutexGroups.get( groupID )
		if mutexGroup and pyRoot in mutexGroup :
			mutexGroup.remove( pyRoot )
			pyRoot.mtxMgr_mutexGroups.remove( groupID )
			if not len( pyRoot.mtxMgr_mutexGroups ) :
				del pyRoot.mtxMgr_mutexGroups


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBeforeRootShow( self, pyRoot ) :
		"""
		窗口显示之前触发
		"""
		self.__doRootMutexShow( pyRoot )

	def __doRootMutexShow( self, pyRoot ) :
		"""
		某个窗口显示时，执行窗口所在互斥组的互斥操作
		"""
		for groupID in pyRoot.mtxMgr_mutexGroups :
			mutexGroup = self.__mutexGroups.get( groupID )
			if mutexGroup and pyRoot in mutexGroup :
				for pyMutexUI in mutexGroup :
					if pyMutexUI.visible and pyMutexUI != pyRoot :
						pyMutexUI.hide()
			elif mutexGroup is None  :
				raise IndexError( "No such group of No: %s!" % groupID )
			else :
				raise ValueError( "%s is not in group %s !" % ( str( pyRoot ), groupID ) )


mutexShowMgr = MutexShowMgr()
