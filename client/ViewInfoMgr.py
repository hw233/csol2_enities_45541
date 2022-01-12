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

		self.__defSettingSect = None							# ������Ϣ section������ section ��Ŀ���Ǳ��Ᵽ�����ı�����
		self.__userSettingSect = None							# �û����� section����Ϊ��ȡ��Ƶ���������Ҫʱ�ٴ� section ��ȡ��
		self.__userSettingPath = ""								# �û���������·��
		self.__tmpSetting = {}									# ��ʱ���ã�{ ( ������Ϣ��, ������ ) : ����ֵ } }
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
		��ȡĬ������ֵ
		"""
		sect = self.__defSettingSect[infoKey]
		if sect is None :
			raise KeyError( "infoKey '%s' of viewInfo is not exist!" % infoKey )
		sect = sect[itemKey]
		if sect is None :
			raise KeyError( "itemKey '%s' in viewInfo '%s' is not exist!" % ( itemKey, infoKey ) )
		itype = sect.readString( "type" ).lower()					# Ҫ���õ�����
		rFunc = "read" + itype.capitalize()							# Language ������ֵ��ȡ����
		return getattr( sect, rFunc )( "def" )

	def __getUserSetting( self, infoKey, itemKey ) :
		"""
		��ȡ�û�����ֵ���������򷵻� None
		"""
		infoSect = self.__defSettingSect[infoKey]
		if infoSect is None :
			ERROR_MSG( "info key %s is not exist!" % infoKey )
			return
		defSect = infoSect[itemKey]
		if defSect is None :
			ERROR_MSG( "item key %s is not exist!" % itemKey )
			return
		itype = defSect.readString( "type" ).lower()				# Ҫ���õ�����
		rFunc = "read" + itype.capitalize()							# Language ������ֵ��ȡ����
		sect = self.__userSettingSect[infoKey]
		if sect is None or sect[itemKey] is None :					# ����û�û������
			return None
		return getattr( sect, rFunc )( itemKey )

	def __getOrignSetting( self, infoKey, itemKey ) :
		"""
		��ȡ���øı�ǰ������ֵ
		"""
		usetting = self.__getUserSetting( infoKey, itemKey )
		if usetting is not None : return usetting
		return self.__getDefSetting( infoKey, itemKey )

	# -------------------------------------------------
	def __getTempSetting( self, infoKey, itemKey ) :
		"""
		��ȡ��ʱ����ֵ���������򷵻� None
		"""
		if self.__tmpSetting.has_key( ( infoKey, itemKey ) ) :		# �鿴�Ƿ�����ʱ���ã�δ��������ã�
			return self.__tmpSetting[( infoKey, itemKey )]			# ���򷵻���ʱ����ֵ
		return None

	# -------------------------------------------------
	def __saveSetting( self, infoKey, itemKey, value ) :
		"""
		Ӧ��ָ������
		"""
		defSect = self.__defSettingSect[infoKey][itemKey]
		itype = defSect.readString( "type" ).lower()				# Ҫ���õ�����
		wFunc = "write" + itype.capitalize()						# Language ������ֵ��ȡ����
		sect = self.__userSettingSect[infoKey]
		if sect is None :											# ����û����ò�����
			sect = self.__userSettingSect.createSection( infoKey )	# �򴴽�һ���û�����
		elif sect[itemKey] :										# ����û����ô���
			sect.deleteSection( itemKey )							# ����ɾ��ԭ��������
		if self.__getDefSetting( infoKey, itemKey ) != value :		# ֻ�����õ�ֵ������Ĭ��ֵ
			getattr( sect, wFunc )( itemKey, value )				# ����������


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		��ɫ��������ʱ������
		"""
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__userSettingPath = "account/%s/%s/viewinfosetting.xml" % ( accountName, roleName )
		self.__userSettingSect = ResMgr.openSection( self.__userSettingPath, True )

	def onRoleLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		Language.purgeConfig( self.__userSettingPath )
		self.__userSettingPath = ""
		self.__tmpSetting = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSetting( self, infoKey, itemKey ) :
		"""
		��ȡ�û�����ֵ
		"""
		value = self.__getTempSetting( infoKey, itemKey )			# ��ȡ��ʱ����ֵ
		if value is not None : return value
		return self.__getOrignSetting( infoKey, itemKey )			# ���򷵻�Ĭ������ֵ

	def changeSetting( self, infoKey, itemKey, value ) :
		"""
		�������ã������棩
		"""
		oldValue = self.getSetting( infoKey, itemKey )
		self.__tmpSetting[( infoKey, itemKey )] = value				# �����øı���ӵ���ʱ����
		if oldValue == value : return
		ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
			infoKey, itemKey, oldValue, value )						# �������ø�����Ϣ

	# -------------------------------------------------
	def setToDefault( self, infoKey, itemKey ) :
		"""
		��ָ����������ΪĬ��ֵ�������棨���ú���Ҫ���� save ���ܱ��浽��棩
		"""
		for itemKey, itemSect in self.__defSettingSect[infoKey].items() :		# ����ָ�����õ�������
			defValue = self.__getDefSetting( infoKey, itemKey )					# ��ȡ��Ĭ��ֵ
			currValue = self.getSetting( infoKey, itemKey )						# ��ǰ����ֵ
			if currValue == defValue : continue									# ��ǰ����ֵ������Ĭ��ֵ
			self.__tmpSetting[( infoKey, itemKey )] = defValue
			ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
				infoKey, itemKey, currValue, defValue )							# ���򣬴������ø�����Ϣ

		if self.__userSettingSect[infoKey] is not None :						# ��������û�����
			self.__userSettingSect.deleteSection( infoKey )						# ������û�����

	def setAllToDefault( self ) :
		"""
		ȫ������ΪĬ��ֵ�����ú���Ҫ���� save ���ܱ��浽��棩
		"""
		for infoKey, subData in self.__defSettingSect.items() :
			for itemKey in subData.keys():
				self.setToDefault( infoKey, itemKey )

	# -------------------------------------------------
	def cancel( self ) :
		"""
		ȡ������
		"""
		tempDict = dict( self.__tmpSetting )
		self.__tmpSetting = {}													# �����ʱ�����б�
		for ( infoKey, itemKey ), value in tempDict.iteritems() :
			orignValue = self.__getOrignSetting( infoKey, itemKey )
			if orignValue == value : continue
			ECenter.fireEvent( "EVT_ON_VIEWINFO_CHANGED", \
				infoKey, itemKey, value, orignValue )							# ���򴥷����ø�����Ϣ

	def save( self ) :
		"""
		�����û�����
		"""
		for ( infoKey, itemKey ), value in self.__tmpSetting.iteritems() :
			defValue = self.__getDefSetting( infoKey, itemKey )					# Ĭ������
			usrValue = self.__getUserSetting( infoKey, itemKey )				# �û�����
			if value == defValue :												# ���������ֵ��Ĭ��ֵһ��
				if usrValue is not None :
					self.__userSettingSect[infoKey].deleteSection( itemKey )	# ��ɾ���û�����
					if len( self.__userSettingSect[infoKey].items() ) == 0 :	# ������û�����ֵ���������Ѿ�û������
						self.__userSettingSect.deleteSection( infoKey )			# ��ɾ�����������
			elif value != usrValue :											# ���������ֵ��Ĭ��ֵ��һ��
				self.__saveSetting( infoKey, itemKey, value )					# �򱣴�������ֵ���û�����
		self.__tmpSetting = {}													# �����ʱ�����б�
		self.__userSettingSect.save()


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
viewInfoMgr = ViewInfoMgr.instance()
