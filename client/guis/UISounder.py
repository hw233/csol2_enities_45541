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
		self.__pyUIs = WeakList()							# ���沥��ͬһ������UI ·��Ҳһ�������� UI

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
		����Ӧ�� UI ���¼�������ʱ����
		"""
		soundPath = "ui/%s" % self.__sound
		BigWorld.callback( 0.001, Functor( rds.soundMgr.playUI, soundPath ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setCarrier( self, pyRoot ) :
		"""
		���ö�Ӧ�� UI������ UI ���¼���ʹ���¼���Ϣ����ʱ����������
		�ɹ��򷵻� True��ʧ���򷵻� False
		"""
		ui = pyRoot.getGui()								# ��ȡ���� UI
		segUIPath = self.segUIPath							# UI ·��
		while len( segUIPath ) :							# ѭ������·��
			name = segUIPath.pop( 0 )						# ·���ϵ� UI ����
			subUI = getattr( ui, name, None )				# ��ȡ·���ϵ�ĳ������ UI
			if subUI is None : return False					# ����Ҳ�������ʧ�ܷ���
			ui = subUI										# ������һ��
		pyUI = UIScriptWrapper.unwrap( ui )
		if pyUI is None : return False
		if pyUI in self.__pyUIs : return True				# �������Ѿ�����
		event = getattr( pyUI, self.__eventName, None )		# ��ȡ UI ���¼�
		if event is None : return False						# �¼���������ʧ�ܷ���
		event.bind( self.__eventTrigger )					# ������¼�
		self.__pyUIs.append( pyUI )							# ��ӵ� UI �б���
		return True											# �������óɹ�

	def isUsed( self ) :
		"""
		��ȡ�Ƿ��Ѿ�ʹ��
		"""
		return len( self.__pyUIs ) > 0

	# ---------------------------------------
	def resetSound( self, sound ) :
		"""
		������������
		"""
		self.__sound = sound


# --------------------------------------------------------------------
# implement ui sounder manager class
# --------------------------------------------------------------------
class UISounder( Singleton ) :
	__cc_config = "config/client/uisounds.py"

	def __init__( self ) :
		self.__soundInfos = {}					# ������Ϣ�б�: { ( hookName, uiPath ) : { "eventName" : �¼�����, "sound" : �����ļ����� } }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __getUIPath( pyUI ) :
		"""
		��ȡ UI ��·��
		"""
		hookName = pyUI.pyTopParent.hookName	# ��� hookName

		pathUIs = [pyUI.getGui()]				# �� pyUI ·���ϵ����� UI���� pyUI ���������� UI��
		parent = pyUI.getGui().parent			# ��ȡ pyUI �ĸ� UI
		while parent :							# ѭ����ȡ pyUI �����и� UI
			pathUIs.append( parent )
			parent = parent.parent
		segUIPath = []							# ���� pyUI �����и� UI ������
		ui = pathUIs.pop()						# ������������ UI
		while len( pathUIs ) :					# ѭ���ҳ��������� UI ������
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
		����һ��������ӵ� UI ������ʱ������
		"""
		if pyRoot.hookName == "" : return
		pyRoot.tmp_initialize_sound = False							# ����һ����ʱ����������Ƿ��ʼ����������


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		��ʼ��( ����Դ���������� )
		"""
		config = PyConfiger().read( self.__cc_config, {}, True )
		for ( hookName, uiPath, eventName ), sound in config.items() :
			soundInfo = SoundInfo( hookName, uiPath, eventName, sound )
			self.__soundInfos[( hookName, uiPath, eventName )] = soundInfo

	def initRootSound( self, pyRoot ) :
		"""
		��ʼ�� Root UI ������( ���ڵ�һ�δ�ʱ������ )
		"""
		if not hasattr( pyRoot, "tmp_initialize_sound" ) :
			return
		del pyRoot.tmp_initialize_sound
		for ( hookName, uiPath, eventName ), soundInfo in \
			self.__soundInfos.items() :											# ���������������õ�Ŀ���ǣ���ֹ��Щ UI ɾ���ˣ�������ûɾ
				if soundInfo.hookName != pyRoot.hookName :
					continue
				if not soundInfo.setCarrier( pyRoot ) : 						# �� UI �����Ĵ����������¼�
					self.__soundInfos.pop( ( hookName, uiPath, eventName ) )	# �����ʧ�ܣ�����б��н�������Ϣȥ��


	# -------------------------------------------------
	# ��ȡ������һ�� UI ������
	# -------------------------------------------------
	def getSoundInfos( self, pyUI ) :
		"""
		��ȡһ�� UI �������¼�����
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
		����һ�� UI ������
		"""
		if pyUI.pyTopParent is None :									# �� topParent �����ж�Ӧ�� python UI
			ERROR_MSG( "ui's top parent must bind a python ui" )
			return False
		if pyUI.pyTopParent.hookName == "" :							# topParent ����Ҫ�� hookName
			ERROR_MSG( "ui's top parent must contain a hook name" )
			return False
		hookName, uiPath = self.__getUIPath( pyUI )						# ���� UI ·��
		eventName = event.getEventName()								# ��ȡ�¼�����
		key = ( hookName, uiPath, eventName )
		soundInfo = self.__soundInfos.get( key, None )
		if soundInfo :
			soundInfo.resetSound( sound )								# ����ҵ�����������������
		else :
			soundInfo = SoundInfo( hookName, uiPath, eventName, sound )
			self.__soundInfos[key] = soundInfo

		if soundInfo.setCarrier( pyUI.pyTopParent ) :					# ��������ԶΪ True
			INFO_MSG( "set ui sound successfully! create a new soundInfo." )
			return True													# �ɹ�����
		return False

	def removeUIEventSounds( self, pyUI, eventNames ) :
		"""
		ɾ��һ��������Ϣ
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
