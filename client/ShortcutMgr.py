
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
		self.__tag = defSect.readString( "tag" )						# ��ݼ����
		strStatus = defSect.readString( "status" )
		self.__status = getattr( Define, strStatus, Define.GST_NONE )	# ��ݼ�����״̬
		strPri = defSect.readString( "pri" )
		self.__pri = getattr( SC_PRI, strPri )							# ��ݼ����ȼ�
		self.__allKeyHandle = defSect.readInt( "allKeyHandle" )			# �Ƿ�������а����¼�
		self.__comment = defSect.readString( "comment" )				# ��ݼ�˵��

		self.__down = defSect.readInt( "down" )							# ����״̬
		self.__unionKeys = []											# ��ݼ�
		self.__handler = None											# ��ݼ�������

		self.__defSect = defSect										# Ĭ�Ͽ�ݼ�����
		self.__customSect = None										# �û���ݼ�����

		self.__shortcutChangeCallback = None							# ��ݼ��ı�ʱ���ᱻ��������Ϊ��֪ͨ������¿�ݼ�����������Ʋ��ã�

		self.custom = False												# ��ݼ��Ƿ������û�����
		self.setTempDefault()											# ��������ΪĬ�Ͽ�ݼ�


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def tag( self ) :
		"""
		��ݼ����
		"""
		return self.__tag

	@property
	def unionKeys( self ) :
		"""
		��ݼ�
		"""
		return self.__unionKeys[:]

	@property
	def status( self ) :
		"""
		Ӧ��״̬
		"""
		return self.__status

	@property
	def pri( self ) :
		"""
		��ݼ����ȼ�
		"""
		return self.__pri

	@property
	def allKeyHandle( self ) :
		"""
		�Ƿ����ȫ��������Ϣ
		"""
		return self.__allKeyHandle

	@property
	def shortcutString( self ) :
		"""
		����
		"""
		return keys.shortcutToString( self.key, self.mods )

	@property
	def comment( self ) :
		return self.__comment

	# -------------------------------------------------
	# ���ص�һ���ݼ��İ�����Ϣ
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
		��ȡĬ�ϵļ����
		"""
		unionKeys = []
		for tag, sect in self.__defSect["keys"].items() :
			strKey = sect.readString( "key" )
			strMods = sect.readString( "mods" ).split( "," )
			key = getattr( keys, strKey, 0 )					# ���µļ�
			mods = 0											# ���Ӽ�
			for strMod in strMods :
				mods |= getattr( keys, strMod.strip(), 0 )
			unionKeys.append( ( key, mods ) )
		if len( unionKeys ) == 0 :
			unionKeys = [( 0, 0 )]
		return unionKeys

	def __setUnionKeys( self, unionKeys ) :
		"""
		���ÿ�ݼ�
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
		���ÿ�ݼ��ı�ص�
		"""
		self.__shortcutChangeCallback = RefEx( callback )
		self.__setUnionKeys( self.__unionKeys )								# ���ú󴥷�һ�ο�ݼ��ı�ص�

	def setCustomSect( self, sect ) :
		"""
		�����û������ݼ�
		"""
		self.__customSect = sect
		if sect is not None :												# ����Ϊ�û����ÿ�ݼ�
			key = sect.readInt( "key" )
			mods = sect.readInt( "mods" )
			self.__setUnionKeys( [( key, mods )] )
		else :																# �ָ�ΪĬ�Ͽ�ݼ�
			self.__setUnionKeys( self.__getDefUnionKeys() )

	def setHandler( self, handler ) :
		"""
		��һ����ݼ�����
		"""
		self.__handler = RefEx( handler )

	# -------------------------------------------------
	def setTempDefault( self ) :
		"""
		��ʱ����ΪĬ�Ͽ�ݼ�
		"""
		self.__setUnionKeys( self.__getDefUnionKeys() )

	def setTempUnionKey( self, key, mods ) :
		"""
		��ʱ���ÿ�ݼ�
		"""
		self.__setUnionKeys( [( key, mods )] )

	# ---------------------------------------
	def cancelTemp( self ) :
		"""
		ȡ����ʱ����
		"""
		self.setCustomSect( self.__customSect )

	def applyTemp( self ) :
		"""
		Ӧ����ʱ����
		"""
		defUnion = self.__getDefUnionKeys()								# Ĭ�Ͽ�ݼ�
		if self.__unionKeys == defUnion :								# �����ǰ���õĿ�ݼ��պõ���Ĭ�Ͽ�ݼ�
			if self.__customSect is not None :
				ShortcutMgr.cg_customSect.deleteSection( self.tag )		# ��ɾ���û����ÿ�ݼ�
				self.__customSect = None
			return

		if self.__customSect is not None :
			ShortcutMgr.cg_customSect.deleteSection( self.tag )			# ���򣬴����û�����
		key, mods = self.__unionKeys[0]
		sect = ShortcutMgr.cg_customSect.createSection( self.tag )
		sect.writeInt( "key", key )
		sect.writeInt( "mods", mods )
		self.__customSect = sect

	# -------------------------------------------------
	def trigger( self, down, key, mods ) :
		"""
		������ݼ�����
		"""
		if not self.__handler or not self.__handler() :		# û�а���Ӧ�Ŀ�ݼ����պ���
			return False
		if self.__down == 10 :
			if down == 0 : return False						# ��Ҫ�ͷŰ���������ǰ������
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
		�ͷŰ���
		"""
		if not self.__handler or not self.__handler() :		# û�а���Ӧ�Ŀ�ݼ����պ���
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
	cg_customSect = None							# �û����ø� Section

	def __init__( self ) :
		self.__shortcuts = {}						# { ��ݼ���� : SCInfo ʵ�� } }
		self.__statusTags = {}						# { ״̬ : ��ݼ���� }
		self.__needReleaseSCs = {}					# ��Ҫ�ڰ�������ʱ�����Ŀ�ݼ�{ ״̬ : ��ݼ���� }
		self.__customPath = ""						# �û���������·��
		self.__skillBar = []
		
		self.__classifySCs = MapList()				# ��ݼ������

		self.__initShortcuts()						# ��ʼ����ݼ���
		self.__initShortcutTypes()					# ��ʼ����ݼ����ͱ�


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initShortcuts( self ) :
		"""
		��ʼ����ݼ���
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
			for st in Define.GST_UNBUSYS :									# ���Ƿ�æ״̬�µĿ�ݼ��ֱ�ŵ����Ե�״̬�б���
				if st in self.__statusTags :
					self.__statusTags[st] += unbusySCInfos.keys()
				else :
					self.__statusTags[st] = unbusySCInfos.keys()

		self.__needReleaseSCs = {}
		for status, tags in self.__statusTags.iteritems() :						# ��ͬһ״̬�µĿ�ݼ������ȼ�����
			tags.sort( key = lambda tag : self.__shortcuts[tag].pri )
			self.__needReleaseSCs[status] = []
			for tag in tags :
				scInfo = self.__shortcuts[tag]
				if scInfo.down == 10 :
					self.__needReleaseSCs[status].append( scInfo )

	def __initShortcutTypes( self ) :
		"""
		��ʼ����ݼ�����
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
				scInfo.custom = True							# �ҵ���Ӧ�� ShortcutInfo
				self.__classifySCs[typeName].append( scInfo )
				if isSkillbar:
					self.__skillBar.append(scInfo)
		Language.openConfigSection( path )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		��ɫ��������ʱ������
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
		��ɫ�뿪����ʱ������
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
		��ȡ���пɱ��û����õĿ�ݼ�
		"""
		return self.__classifySCs

	def getSkillbarSC(self):
		"""
		��ÿ�ݼ��������
		"""
		return self.__skillBar
	# -------------------------------------------------
	def setHandler( self, scTag, handler ) :
		"""
		��һ����ݼ�����
		"""
		try :
			self.__shortcuts[scTag].setHandler( handler )
		except :
			EXCEHOOK_MSG()

	# -------------------------------------------------
	def getShortcutInfo( self, scTag ) :
		"""
		��ȡ��ݼ�
		"""
		if self.__shortcuts.has_key( scTag ):
			return self.__shortcuts[scTag]

	# ---------------------------------------
	def getShortcutViaKey( self, pri, key, mods ) :
		"""
		��ȡ������Ӧ�Ŀ�ݼ���Ϣ����� onlyCustom Ϊ�棬��ֻ�ӿ��û����ÿ�ݼ���Ѱ��
		ע���� ֻ��Ѱ GST_IN_WORD �µĿ�ݼ�
			�� ������ͬ��Ȩ�޲�ͬ����Ϊ��ͬ
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
		���ÿ�ݼ�
		ע��������� key == 0�����ʾ��ݼ�Ϊ��δ���á�
		"""
		if self.__shortcuts.has_key( scTag ):
			self.__shortcuts[scTag].setTempUnionKey( key, mods )

	def setToDefault( self, scTag ) :
		"""
		����ĳ����ݼ�ΪĬ��ֵ
		"""
		self.__shortcuts[scTag].setTempDefault()

	def setAllToDefault( self ) :
		"""
		��ȫ����ݼ�����ΪĬ��ֵ
		"""
		for tag, scInfo in self.__shortcuts.iteritems() :
			scInfo.setTempDefault()

	def cancel( self, scTag = None ) :
		"""
		ȡ����ݼ����ã���� scTag �� None����ȡ��ȫ����ݼ�����ʱ����
		"""
		if scTag is None :
			for tag, scInfo in self.__shortcuts.iteritems() :
				scInfo.cancelTemp()
		else :
			self.__shortcuts[scTag].cancelTemp()

	def save( self ) :
		"""
		�����ݼ�����
		"""
		if ShortcutMgr.cg_customSect is None : return
		for tag, scInfo in self.__shortcuts.iteritems() :
			scInfo.applyTemp()
		self.cg_customSect.save()

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		���հ�����Ϣ
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
		�ͷſ�ݼ�( down ֵΪ 10 �ģ���ʾ����Ҫ�ڰ�������ʱ�ͷŵĿ�ݼ� )
		ע������ӿڵ�����ƺ���������������Ϊ���ͷŽ�ɫ���߼�����Ƶģ�
			�����û������ӿڣ��ܿ���ĳЩ����£�������ͷź󣬽�ɫ���������ǰ�ߡ�
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
