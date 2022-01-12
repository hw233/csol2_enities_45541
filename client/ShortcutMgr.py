
# -*- coding: gb18030 -*-
#
# $Id: ShortcutMgr.py,v 1.68 2008-09-02 09:57:22 fangpengjun Exp $

"""
implement all shortcuts of the game system
--2007/08/09 : writen by huangyongwei
--2008/11/05 : rewriten by huangyongwei( used default shortcut config )
"""

import sys
import copy
import Language
import ResMgr
import keys
import Define
from bwdebug import *
from cscollections import MapList
from Weaker import RefEx
from keys import *
from AbstractTemplates import Singleton
from gbref import rds
import event.EventCenter as ECenter

# --------------------------------------------------------------------
# implement shortcut priorities
# --------------------------------------------------------------------
class SC_PRI :
	L1		= 1
	L2		= 2
	L3		= 3
	L4		= 4
	L5		= 5


# --------------------------------------------------------------------
# implement shortcut information
# --------------------------------------------------------------------
class SCInfo( object ) :
	def __init__( self, defSect ) :
		self.__tag = defSect.readString( "tag" )						# 快捷键标记
		strStatus = defSect.readString( "status" )
		self.__status = getattr( Define, strStatus, Define.GST_NONE )	# 快捷键工作状态
		strPri = defSect.readString( "pri" )
		self.__pri = getattr( SC_PRI, strPri )							# 快捷键优先级
		self.__allKeyHandle = defSect.readInt( "allKeyHandle" )			# 是否接收所有按键事件
		self.__comment = defSect.readString( "comment" )				# 快捷键说明

		self.__down = defSect.readInt( "down" )							# 按下状态
		self.__unionKeys = []											# 快捷键
		self.__handler = None											# 快捷键处理函数

		self.__defSect = defSect										# 默认快捷键配置
		self.__customSect = None										# 用户快捷键配置

		self.__shortcutChangeCallback = None							# 快捷键改变时将会被触发（这为了通知界面更新快捷键－－这样设计不好）

		self.custom = False												# 快捷键是否允许用户设置
		self.setTempDefault()											# 首先设置为默认快捷键


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def tag( self ) :
		"""
		快捷键标记
		"""
		return self.__tag

	@property
	def unionKeys( self ) :
		"""
		快捷键
		"""
		return self.__unionKeys[:]

	@property
	def status( self ) :
		"""
		应用状态
		"""
		return self.__status

	@property
	def pri( self ) :
		"""
		快捷键优先级
		"""
		return self.__pri

	@property
	def allKeyHandle( self ) :
		"""
		是否接受全部按键消息
		"""
		return self.__allKeyHandle

	@property
	def shortcutString( self ) :
		"""
		键名
		"""
		return keys.shortcutToString( self.key, self.mods )

	@property
	def comment( self ) :
		return self.__comment

	# -------------------------------------------------
	# 返回第一组快捷键的按键信息
	# -------------------------------------------------
	@property
	def down( self ) :
		return self.__down

	@property
	def key( self ) :
		return self.__unionKeys[0][0]

	@property
	def mods( self ) :
		return self.__unionKeys[0][1]


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getDefUnionKeys( self ) :
		"""
		获取默认的键组合
		"""
		unionKeys = []
		for tag, sect in self.__defSect["keys"].items() :
			strKey = sect.readString( "key" )
			strMods = sect.readString( "mods" ).split( "," )
			key = getattr( keys, strKey, 0 )					# 按下的键
			mods = 0											# 附加键
			for strMod in strMods :
				mods |= getattr( keys, strMod.strip(), 0 )
			unionKeys.append( ( key, mods ) )
		if len( unionKeys ) == 0 :
			unionKeys = [( 0, 0 )]
		return unionKeys

	def __setUnionKeys( self, unionKeys ) :
		"""
		设置快捷键
		"""
		self.__unionKeys = unionKeys
		if self.__shortcutChangeCallback :
			callback = self.__shortcutChangeCallback()
			if callback :
				callback( self )
				key, mods = unionKeys[0]
				keyStr = keys.shortcutToString( key, mods )
				ECenter.fireEvent( "EVT_ON_TEMP_SHORTCUT_TAG_SET", self.__tag, keyStr )

	# -------------------------------------------------
	def __doHandle( self, down, key, mods ) :
		if self.__handler is None : return False
		try :
			handle = self.__handler()
			vars = []
			vs = handle.func_code.co_varnames
			if "down" in vs : vars.append( down )
			if "key" in vs : vars.append( key )
			if "mods" in vs : vars.append( mods )
			return handle( *vars )
		except :
			EXCEHOOK_MSG()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setShortcutChangeCallback( self, callback ) :
		"""
		设置快捷键改变回调
		"""
		self.__shortcutChangeCallback = RefEx( callback )
		self.__setUnionKeys( self.__unionKeys )								# 设置后触发一次快捷键改变回调

	def setCustomSect( self, sect ) :
		"""
		设置用户定义快捷键
		"""
		self.__customSect = sect
		if sect is not None :												# 更新为用户设置快捷键
			key = sect.readInt( "key" )
			mods = sect.readInt( "mods" )
			self.__setUnionKeys( [( key, mods )] )
		else :																# 恢复为默认快捷键
			self.__setUnionKeys( self.__getDefUnionKeys() )

	def setHandler( self, handler ) :
		"""
		绑定一个快捷键函数
		"""
		self.__handler = RefEx( handler )

	# -------------------------------------------------
	def setTempDefault( self ) :
		"""
		临时设置为默认快捷键
		"""
		self.__setUnionKeys( self.__getDefUnionKeys() )

	def setTempUnionKey( self, key, mods ) :
		"""
		临时设置快捷键
		"""
		self.__setUnionKeys( [( key, mods )] )

	# ---------------------------------------
	def cancelTemp( self ) :
		"""
		取消临时设置
		"""
		self.setCustomSect( self.__customSect )

	def applyTemp( self ) :
		"""
		应用临时设置
		"""
		defUnion = self.__getDefUnionKeys()								# 默认快捷键
		if self.__unionKeys == defUnion :								# 如果当前设置的快捷键刚好等于默认快捷键
			if self.__customSect is not None :
				ShortcutMgr.cg_customSect.deleteSection( self.tag )		# 则，删除用户设置快捷键
				self.__customSect = None
			return

		if self.__customSect is not None :
			ShortcutMgr.cg_customSect.deleteSection( self.tag )			# 否则，创建用户配置
		key, mods = self.__unionKeys[0]
		sect = ShortcutMgr.cg_customSect.createSection( self.tag )
		sect.writeInt( "key", key )
		sect.writeInt( "mods", mods )
		self.__customSect = sect

	# -------------------------------------------------
	def trigger( self, down, key, mods ) :
		"""
		触发快捷键函数
		"""
		if not self.__handler or not self.__handler() :		# 没有绑定相应的快捷键接收函数
			return False
		if self.__down == 10 :
			if down == 0 : return False						# 需要释放按键，但当前是提起
		elif self.__down != down :
			return False
		if self.__allKeyHandle :
			return self.__doHandle( down, key, mods )
		for mkey, mmods in self.__unionKeys :
			if key != mkey : continue
			if mods != mmods : continue
			return self.__doHandle( down, key, mods )
		return False

	def release( self, key, mods ) :
		"""
		释放按键
		"""
		if not self.__handler or not self.__handler() :		# 没有绑定相应的快捷键接收函数
			return False
		if self.__allKeyHandle :
			return self.__doHandle( 0, key, mods )
		for mkey, mmods in self.__unionKeys :
			if key != mkey : continue
			if mods != mmods : continue
			return self.__doHandle( 0, key, mods )
		return False


# --------------------------------------------------------------------
# implement shortcut manager
# --------------------------------------------------------------------
class ShortcutMgr( Singleton ) :
	cg_customSect = None							# 用户设置根 Section

	def __init__( self ) :
		self.__shortcuts = {}						# { 快捷键标记 : SCInfo 实例 } }
		self.__statusTags = {}						# { 状态 : 快捷键标记 }
		self.__needReleaseSCs = {}					# 需要在按键提起时触发的快捷键{ 状态 : 快捷键标记 }
		self.__customPath = ""						# 用户设置配置路径
		self.__skillBar = []
		
		self.__classifySCs = MapList()				# 快捷键分类表

		self.__initShortcuts()						# 初始化快捷键表
		self.__initShortcutTypes()					# 初始化快捷键类型表


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initShortcuts( self ) :
		"""
		初始化快捷键表
		"""
		path = "config/client/shortcuts.xml"
		sect = Language.openConfigSection( path )
		unbusySCInfos = {}
		for tag, subSect in sect.items() :
			scInfo = SCInfo( subSect )
			scTag = scInfo.tag
			self.__shortcuts[scTag] = scInfo
			status = scInfo.status
			if status == Define.GST_UNBUSY :
				unbusySCInfos[scTag] = scInfo
			elif status in self.__statusTags :
				self.__statusTags[status].append( scTag )
			else :
				self.__statusTags[status] = [scTag]
		Language.purgeConfig( path )

		if len( unbusySCInfos ) :
			for st in Define.GST_UNBUSYS :									# 将非繁忙状态下的快捷键分别放到各自的状态列表中
				if st in self.__statusTags :
					self.__statusTags[st] += unbusySCInfos.keys()
				else :
					self.__statusTags[st] = unbusySCInfos.keys()

		self.__needReleaseSCs = {}
		for status, tags in self.__statusTags.iteritems() :						# 对同一状态下的快捷键按优先级排序
			tags.sort( key = lambda tag : self.__shortcuts[tag].pri )
			self.__needReleaseSCs[status] = []
			for tag in tags :
				scInfo = self.__shortcuts[tag]
				if scInfo.down == 10 :
					self.__needReleaseSCs[status].append( scInfo )

	def __initShortcutTypes( self ) :
		"""
		初始化快捷键类别表
		"""
		path = "config/client/shortcuttypes.xml"
		sect = Language.openConfigSection( path )
		for tag, subSect in sect.items() :
			typeName = subSect.asString
			tags = subSect.readStrings( "item" )
			self.__classifySCs[typeName] = []
			isSkillbar = False
			if tag == "quikbar":
				isSkillbar = True
			for tag in tags :
				scInfo = self.__shortcuts[tag]
				scInfo.custom = True							# 找到对应的 ShortcutInfo
				self.__classifySCs[typeName].append( scInfo )
				if isSkillbar:
					self.__skillBar.append(scInfo)
		Language.openConfigSection( path )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		角色进入世界时被调用
		"""
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__customPath = "account/%s/%s/shortcuts.xml" % ( accountName, roleName )
		ShortcutMgr.cg_customSect = ResMgr.openSection( self.__customPath, True )
		for tag, subSect in self.cg_customSect.items() :
			scInfo = self.__shortcuts.get( tag, None )
			if scInfo :
				scInfo.setCustomSect( subSect )
			else :
				ShortcutMgr.cg_customSect.deleteSection( tag )
		self.cg_customSect.save()

	def onRoleLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		for scInfo in self.__shortcuts.itervalues() :
			scInfo.setCustomSect( None )
		if ShortcutMgr.cg_customSect is not None :
			ResMgr.purge( self.__customPath )
			ShortcutMgr.cg_customSect = None
			self.__customPath = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getClassifyShortcuts( self ) :
		"""
		获取所有可被用户设置的快捷键
		"""
		return self.__classifySCs

	def getSkillbarSC(self):
		"""
		获得快捷键技能相关
		"""
		return self.__skillBar
	# -------------------------------------------------
	def setHandler( self, scTag, handler ) :
		"""
		绑定一个快捷键函数
		"""
		try :
			self.__shortcuts[scTag].setHandler( handler )
		except :
			EXCEHOOK_MSG()

	# -------------------------------------------------
	def getShortcutInfo( self, scTag ) :
		"""
		获取快捷键
		"""
		if self.__shortcuts.has_key( scTag ):
			return self.__shortcuts[scTag]

	# ---------------------------------------
	def getShortcutViaKey( self, pri, key, mods ) :
		"""
		获取按键对应的快捷键信息，如果 onlyCustom 为真，则只从可用户设置快捷键中寻找
		注：① 只搜寻 GST_IN_WORD 下的快捷键
			② 按键相同，权限不同，视为不同
		"""
		if key == 0 : return None
		for scTag in self.__statusTags[Define.GST_IN_WORLD] :
			scInfo = self.__shortcuts[scTag]
			if scInfo.status != Define.GST_UNBUSY and \
				scInfo.status != Define.GST_IN_WORLD :
					continue
			unionKeys = scInfo.unionKeys
			for k, m in unionKeys :
				if k == key and m == mods :
					return scInfo
		return None

	# ---------------------------------------
	def setShortcut( self, scTag, key, mods ) :
		"""
		设置快捷键
		注：如果设置 key == 0，则表示快捷键为“未设置”
		"""
		if self.__shortcuts.has_key( scTag ):
			self.__shortcuts[scTag].setTempUnionKey( key, mods )

	def setToDefault( self, scTag ) :
		"""
		设置某个快捷键为默认值
		"""
		self.__shortcuts[scTag].setTempDefault()

	def setAllToDefault( self ) :
		"""
		将全部快捷键设置为默认值
		"""
		for tag, scInfo in self.__shortcuts.iteritems() :
			scInfo.setTempDefault()

	def cancel( self, scTag = None ) :
		"""
		取消快捷键设置，如果 scTag 是 None，则取消全部快捷键的临时设置
		"""
		if scTag is None :
			for tag, scInfo in self.__shortcuts.iteritems() :
				scInfo.cancelTemp()
		else :
			self.__shortcuts[scTag].cancelTemp()

	def save( self ) :
		"""
		保存快捷键设置
		"""
		if ShortcutMgr.cg_customSect is None : return
		for tag, scInfo in self.__shortcuts.iteritems() :
			scInfo.applyTemp()
		self.cg_customSect.save()

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		接收按键消息
		"""
		from guis.ScreenViewer import ScreenViewer
		screenViewer = ScreenViewer()
		status = rds.statusMgr.currStatus()
		if status not in self.__statusTags :
			return False
		scTags = self.__statusTags[status]
		for tag in scTags :
			if tag.startswith( "UI_TOGGLE" ) and \
			tag != "UI_TOGGLE_ALL_UIS" and \
			screenViewer.isEmptyScreen() and \
			key != KEY_ESCAPE:
				continue
			scInfo = self.__shortcuts[tag]
			if scInfo.trigger( down, key, mods ) :
				return True
		return False

	def releaseShortcut( self, down, key, mods ) :
		"""
		释放快捷键( down 值为 10 的，表示是需要在按键提起时释放的快捷键 )
		注：这个接口的设计似乎不大合理，这仅仅是为了释放角色行走键而设计的，
			但如果没有这个接口，很可能某些情况下，方向键释放后，角色还会继续往前走。
		"""
		if down : return
		status = rds.statusMgr.currStatus()
		scInfos = self.__needReleaseSCs.get( status, [] )
		for scInfo in scInfos :
			scInfo.release( key, mods )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
shortcutMgr = ShortcutMgr()
