# -*- coding: gb18030 -*-
#
# $Id: UISounder.py,v 1.4 2008-06-21 02:09:04 huangyongwei Exp $

"""
implement ui events are not contained by engine
-- 2008/05/30 : writen by huangyongwei
"""

import BigWorld
import UIScriptWrapper
import Language
from Function import Functor
from bwdebug import *
from AbstractTemplates import Singleton
from Weaker import WeakList
from gbref import rds
from gbref import PyConfiger

class SoundInfo :
	def __init__( self, hookName, uiPath, eventName, sound ) :
		self.__hookName = hookName
		self.__uiPath = uiPath
		self.__eventName = eventName
		self.__sound = sound
		self.__pyUIs = WeakList()							# 保存播放同一声音，UI 路径也一样的所有 UI

	@property
	def hookName( self ) :
		return self.__hookName

	@property
	def uiPath( self ) :
		return self.__uiPath

	@property
	def segUIPath( self ) :
		uiPath = self.__uiPath
		if uiPath == "" : return []
		return uiPath.split( "." )

	@property
	def eventName( self ) :
		return self.__eventName

	@property
	def sound( self ) :
		return self.__sound

	# -------------------------------------------------
	@property
	def pyUIs( self ) :
		return self.__pyUIs[:]


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __eventTrigger( self, pySender, *args ) :
		"""
		当对应的 UI 的事件被触发时调用
		"""
		soundPath = "ui/%s" % self.__sound
		BigWorld.callback( 0.001, Functor( rds.soundMgr.playUI, soundPath ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setCarrier( self, pyRoot ) :
		"""
		设置对应的 UI，并绑定 UI 的事件，使得事件消息到来时，播放声音
		成功则返回 True，失败则返回 False
		"""
		ui = pyRoot.getGui()								# 获取引擎 UI
		segUIPath = self.segUIPath							# UI 路径
		while len( segUIPath ) :							# 循环遍历路径
			name = segUIPath.pop( 0 )						# 路径上的 UI 名称
			subUI = getattr( ui, name, None )				# 获取路径上的某个引擎 UI
			if subUI is None : return False					# 如果找不到，则失败返回
			ui = subUI										# 继续下一个
		pyUI = UIScriptWrapper.unwrap( ui )
		if pyUI is None : return False
		if pyUI in self.__pyUIs : return True				# 该配置已经存在
		event = getattr( pyUI, self.__eventName, None )		# 获取 UI 的事件
		if event is None : return False						# 事件不存在则失败返回
		event.bind( self.__eventTrigger )					# 否则绑定事件
		self.__pyUIs.append( pyUI )							# 添加到 UI 列表中
		return True											# 返回设置成功

	def isUsed( self ) :
		"""
		获取是否已经使用
		"""
		return len( self.__pyUIs ) > 0

	# ---------------------------------------
	def resetSound( self, sound ) :
		"""
		重新设置声音
		"""
		self.__sound = sound


# --------------------------------------------------------------------
# implement ui sounder manager class
# --------------------------------------------------------------------
class UISounder( Singleton ) :
	__cc_config = "config/client/uisounds.py"

	def __init__( self ) :
		self.__soundInfos = {}					# 声音信息列表: { ( hookName, uiPath ) : { "eventName" : 事件名称, "sound" : 声音文件名称 } }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __getUIPath( pyUI ) :
		"""
		获取 UI 的路径
		"""
		hookName = pyUI.pyTopParent.hookName	# 获得 hookName

		pathUIs = [pyUI.getGui()]				# 在 pyUI 路径上的所有 UI（即 pyUI 的所有祖先 UI）
		parent = pyUI.getGui().parent			# 获取 pyUI 的父 UI
		while parent :							# 循环获取 pyUI 的所有父 UI
			pathUIs.append( parent )
			parent = parent.parent
		segUIPath = []							# 保存 pyUI 的所有父 UI 的名称
		ui = pathUIs.pop()						# 弹出最顶层的祖先 UI
		while len( pathUIs ) :					# 循环找出所有祖先 UI 的名称
			child = pathUIs.pop()
			for name, ch in ui.children :
				if ch == child :
					segUIPath.append( name )
					break
			ui = child
		return ( hookName, ".".join( segUIPath ) )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRootAdded( self, pyRoot ) :
		"""
		当有一个窗口添加到 UI 管理器时被调用
		"""
		if pyRoot.hookName == "" : return
		pyRoot.tmp_initialize_sound = False							# 设置一个临时变量，标记是否初始化了其声音


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		初始化( 被资源加载器调用 )
		"""
		config = PyConfiger().read( self.__cc_config, {}, True )
		for ( hookName, uiPath, eventName ), sound in config.items() :
			soundInfo = SoundInfo( hookName, uiPath, eventName, sound )
			self.__soundInfos[( hookName, uiPath, eventName )] = soundInfo

	def initRootSound( self, pyRoot ) :
		"""
		初始化 Root UI 的声音( 窗口第一次打开时被调用 )
		"""
		if not hasattr( pyRoot, "tmp_initialize_sound" ) :
			return
		del pyRoot.tmp_initialize_sound
		for ( hookName, uiPath, eventName ), soundInfo in \
			self.__soundInfos.items() :											# 遍历所有声音配置的目的是，防止有些 UI 删除了，但配置没删
				if soundInfo.hookName != pyRoot.hookName :
					continue
				if not soundInfo.setCarrier( pyRoot ) : 						# 对 UI 绑定它的触发声音的事件
					self.__soundInfos.pop( ( hookName, uiPath, eventName ) )	# 如果绑定失败，则从列表中将声音信息去掉


	# -------------------------------------------------
	# 获取或设置一个 UI 的声音
	# -------------------------------------------------
	def getSoundInfos( self, pyUI ) :
		"""
		获取一个 UI 的所有事件声音
		"""
		infos = []
		for soundInfo in self.__soundInfos.itervalues() :
			if pyUI in soundInfo.pyUIs :
				eventName = soundInfo.eventName
				sound = soundInfo.sound
				infos.append( ( eventName, sound ) )
		return infos

	def resetSound( self, pyUI, event, sound ) :
		"""
		设置一个 UI 的声音
		"""
		if pyUI.pyTopParent is None :									# 其 topParent 必须有对应的 python UI
			ERROR_MSG( "ui's top parent must bind a python ui" )
			return False
		if pyUI.pyTopParent.hookName == "" :							# topParent 必须要有 hookName
			ERROR_MSG( "ui's top parent must contain a hook name" )
			return False
		hookName, uiPath = self.__getUIPath( pyUI )						# 计算 UI 路径
		eventName = event.getEventName()								# 获取事件名称
		key = ( hookName, uiPath, eventName )
		soundInfo = self.__soundInfos.get( key, None )
		if soundInfo :
			soundInfo.resetSound( sound )								# 如果找到，则重新设置声音
		else :
			soundInfo = SoundInfo( hookName, uiPath, eventName, sound )
			self.__soundInfos[key] = soundInfo

		if soundInfo.setCarrier( pyUI.pyTopParent ) :					# 理论上永远为 True
			INFO_MSG( "set ui sound successfully! create a new soundInfo." )
			return True													# 成功返回
		return False

	def removeUIEventSounds( self, pyUI, eventNames ) :
		"""
		删除一条声音信息
		"""
		for ( hookName, uiPath, eventName ), soundInfo in \
			self.__soundInfos.iteritems() :
				if pyUI not in soundInfo.pyUIs : continue
				if soundInfo.eventName in eventNames :
					self.__soundInfos.pop( ( hookName, uiPath, eventName ) )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiSounder = UISounder()
