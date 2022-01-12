# -*- coding: gb18030 -*-
#
# $Id: ResourceLoader.py,v 1.30 2008-09-03 01:40:09 huangyongwei Exp $

"""
implement view information in world setting manager

2008/10/09: writen by huangyongwei
"""

import Language
import ResMgr
from bwdebug import *
from gbref import rds
from event import EventCenter as ECenter

class ViewInfoMgr :
	__inst = None

	def __init__( self ) :
		assert ViewInfoMgr.__inst is None, "you should use 'instance()' method to access ViewInfoMgr singleton instance."

		self.__defSettingSect = None							# 设置信息 section（保存 section 的目的是避免保存过多的变量）
		self.__userSettingSect = None							# 用户设置 section（因为读取不频繁，因此需要时再从 section 中取）
		self.__userSettingPath = ""								# 用户设置配置路径
		self.__tmpSetting = {}									# 临时设置：{ ( 设置信息键, 设置项 ) : 设置值 } }
		self.__initialize()

	@classmethod
	def instance( SELF ) :
		if not SELF.__inst :
			SELF.__inst = ViewInfoMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		self.__defSettingSect = Language.openConfigSection( "config/client/viewinfosetting.xml" )
		assert self.__defSettingSect is not None, "can't find view information in world setting config file!"

	# -------------------------------------------------
	def __getDefSetting( self, infoKey, itemKey ) :
		"""
		获取默认设置值
		"""
		sect = self.__defSettingSect[infoKey]
		if sect is None :
			raise KeyError( "infoKey '%s' of viewInfo is not exist!" % infoKey )
		sect = sect[itemKey]
		if sect is None :
			raise KeyError( "itemKey '%s' in viewInfo '%s' is not exist!" % ( itemKey, infoKey ) )
		itype = sect.readString( "type" ).lower()					# 要设置的类型
		rFunc = "read" + itype.capitalize()							# Language 的类型值读取函数
		return getattr( sect, rFunc )( "def" )

	def __getUserSetting( self, infoKey, itemKey ) :
		"""
		获取用户设置值，不存在则返回 None
		"""
		infoSect = self.__defSettingSect[infoKey]
		if infoSect is None :
			ERROR_MSG( "info key %s is not exist!" % infoKey )
			return
		defSect = infoSect[itemKey]
		if defSect is None :
			ERROR_MSG( "item key %s is not exist!" % itemKey )
			return
		itype = defSect.readString( "type" ).lower()				# 要设置的类型
		rFunc = "read" + itype.capitalize()							# Language 的类型值读取函数
		sect = self.__userSettingSect[infoKey]
		if sect is None or sect[itemKey] is None :					# 如果用户没有设置
			return None
		return getattr( sect, rFunc )( itemKey )

	def __getOrignSetting( self, infoKey, itemKey ) :
		"""
		获取设置改变前到设置值
		"""
		usetting = self.__getUserSetting( infoKey, itemKey )
		if usetting is not None : return usetting
		return self.__getDefSetting( infoKey, itemKey )

	# -------------------------------------------------
	def __getTempSetting( self, infoKey, itemKey ) :
		"""
		获取临时设置值，不存在则返回 None
		"""
		if self.__tmpSetting.has_key( ( infoKey, itemKey ) ) :		# 查看是否有临时设置（未保存的设置）
			return self.__tmpSetting[( infoKey, itemKey )]			# 有则返回临时设置值
		return None

	# -------------------------------------------------
	def __saveSetting( self, infoKey, itemKey, value ) :
		"""
		应用指定设置
		"""
		defSect = self.__defSettingSect[infoKey][itemKey]
		itype = defSect.readString( "type" ).lower()				# 要设置的类型
		wFunc = "write" + itype.capitalize()						# Language 的类型值读取函数
		sect = self.__userSettingSect[infoKey]
		if sect is None :											# 如果用户设置不存在
			sect = self.__userSettingSect.createSection( infoKey )	# 则创建一个用户设置
		elif sect[itemKey] :										# 如果用户设置存在
			sect.deleteSection( itemKey )							# 则先删除原来的设置
		if self.__getDefSetting( infoKey, itemKey ) != value :		# 只有设置的值不等于默认值
			getattr( sect, wFunc )( itemKey, value )				# 才重新设置


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		角色进入世界时被调用
		"""
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__userSettingPath = "account/%s/%s/viewinfosetting.xml" % ( accountName, roleName )
		self.__userSettingSect = ResMgr.openSection( self.__userSettingPath, True )

	def onRoleLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		Language.purgeConfig( self.__userSettingPath )
		self.__userSettingPath = ""
		self.__tmpSetting = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSetting( self, infoKey, itemKey ) :
		"""
		获取用户设置值
		"""
		value = self.__getTempSetting( infoKey, itemKey )			# 获取临时设置值
		if value is not None : return value
		return self.__getOrignSetting( infoKey, itemKey )			# 否则返回默认设置值

	def changeSetting( self, infoKey, itemKey, value ) :
		"""
		更改设置（不保存）
		"""
		oldValue = self.getSetting( infoKey, itemKey )
		self.__tmpSetting[( infoKey, itemKey )] = value				# 将设置改变添加到临时表中
		if oldValue == value : return
		ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
			infoKey, itemKey, oldValue, value )						# 触发设置更改消息

	# -------------------------------------------------
	def setToDefault( self, infoKey, itemKey ) :
		"""
		将指定设置设置为默认值，不保存（设置后需要调用 save 才能保存到外存）
		"""
		for itemKey, itemSect in self.__defSettingSect[infoKey].items() :		# 遍历指定设置的所有项
			defValue = self.__getDefSetting( infoKey, itemKey )					# 获取项默认值
			currValue = self.getSetting( infoKey, itemKey )						# 当前设置值
			if currValue == defValue : continue									# 当前设置值正好是默认值
			self.__tmpSetting[( infoKey, itemKey )] = defValue
			ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
				infoKey, itemKey, currValue, defValue )							# 否则，触发设置更改消息

		if self.__userSettingSect[infoKey] is not None :						# 如果存在用户设置
			self.__userSettingSect.deleteSection( infoKey )						# 则清除用户设置

	def setAllToDefault( self ) :
		"""
		全部设置为默认值（设置后需要调用 save 才能保存到外存）
		"""
		for infoKey, subData in self.__defSettingSect.items() :
			for itemKey in subData.keys():
				self.setToDefault( infoKey, itemKey )

	# -------------------------------------------------
	def cancel( self ) :
		"""
		取消更改
		"""
		tempDict = dict( self.__tmpSetting )
		self.__tmpSetting = {}													# 清空临时设置列表
		for ( infoKey, itemKey ), value in tempDict.iteritems() :
			orignValue = self.__getOrignSetting( infoKey, itemKey )
			if orignValue == value : continue
			ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
				infoKey, itemKey, value, orignValue )							# 否则触发设置更改消息

	def save( self ) :
		"""
		保存用户设置
		"""
		for ( infoKey, itemKey ), value in self.__tmpSetting.iteritems() :
			defValue = self.__getDefSetting( infoKey, itemKey )					# 默认设置
			usrValue = self.__getUserSetting( infoKey, itemKey )				# 用户设置
			if value == defValue :												# 如果新设置值与默认值一致
				if usrValue is not None :
					self.__userSettingSect[infoKey].deleteSection( itemKey )	# 则，删除用户设置
					if len( self.__userSettingSect[infoKey].items() ) == 0 :	# 如果该用户设置值所属键下已经没有设置
						self.__userSettingSect.deleteSection( infoKey )			# 则删除这个所属键
			elif value != usrValue :											# 如果新设置值与默认值不一致
				self.__saveSetting( infoKey, itemKey, value )					# 则保存新设置值到用户配置
		self.__tmpSetting = {}													# 清空临时更改列表
		self.__userSettingSect.save()


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
viewInfoMgr = ViewInfoMgr.instance()
