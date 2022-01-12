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
	���㴰�ڹ�����
	ע�⣺��ӵ��������е� UI ���������ã�Ҫ�־ñ��洰�ڣ������б���
	"""
	def __init__( self ) :
		self.__segRngs = {}											# UI ����ֶΣ�����ʼ��ȣ�������ȣ�����ʱ����ȣ�
		self.__segRngs[ZSegs.L1] = ( 0.11, 0.19, 0.1 )				# ��һ�㣺���ϲ㣬һ���������� tooltip �����Ŀؼ�
		self.__segRngs[ZSegs.L2] = ( 0.21, 0.29, 0.2 )				# �ڶ��㣺һ�����ڲ˵������Ŀؼ�
		self.__segRngs[ZSegs.L3] = ( 0.31, 0.39, 0.3 )				# �����㣺һ������ always on top �����Ĵ���
		self.__segRngs[ZSegs.L4] = ( 0.41, 0.49, 0.4 )				# ���Ĳ㣺��ͨ����
		self.__segRngs[ZSegs.L5] = ( 0.51, 0.59, 0.5 )				# ����㣺һ������һֱ�������²�� UI

		self.__pyRoots = {}											# �������еĶ��㴰��
		self.__pyRoots[ZSegs.L1] = WeakList()						# �����һ��
		self.__pyRoots[ZSegs.L2] = WeakList()						# ����ڶ���
		self.__pyRoots[ZSegs.L3] = WeakList()						# ���������
		self.__pyRoots[ZSegs.L4] = WeakList()						# ������Ĳ�
		self.__pyRoots[ZSegs.L5] = WeakList()						# ��������

		self.__pyVSRoots = MapList()								# �������пɼ��� UI
		self.__pyVSRoots[ZSegs.L1] = WeakList()						# �����һ��ɼ��Ĵ���
		self.__pyVSRoots[ZSegs.L2] = WeakList()						# ����ڶ���ɼ��Ĵ���
		self.__pyVSRoots[ZSegs.L3] = WeakList()						# ���������ɼ��Ĵ���
		self.__pyVSRoots[ZSegs.L4] = WeakList()						# ������Ĳ�ɼ��Ĵ���
		self.__pyVSRoots[ZSegs.L5] = WeakList()						# ��������ɼ��Ĵ���

		self.__pyActRoot = None										# ���浱ǰ����Ĵ���

		shortcutMgr.setHandler( "FIXED_ORDER_HIDE_WINDOW", self.__orderHideRoots )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __getSubDialogs( pyParent, pyRoot ) :
		"""
		��ȡָ�����ڵ������Ӵ���
		ע�⣺���ָ��ӹ�ϵ�������� UI �����ָ��ӹ�ϵ������ python UI ���㴰�ڵĸ��ӹ�ϵ
		����ÿ����δ��ڵ�˳���ǣ��ִ��� --> ������
		"""
		pyDialogs = {}
		pyTraveleds = []														# ��ʱ�����Ѿ������Ĵ���
		stack = Stack()															# ����һ����ʱջ
		stack.push( pyParent )													# ָ��������ջ
		while stack.size() > 0 :
			pyTop = stack.top()													# ��ȡջ������
			pySubDialogs = pyTop.pySubDialogs
			if pyTop not in pyTraveleds and len( pySubDialogs ) > 0 :			# ���ջ���Ĵ��ڻ�û������
				pyTraveleds.append( pyTop )										# ����ӵ� �Ѿ��������� ��
				pySubDialogs.sort( key = lambda d : d.posZ, reverse = True )	# �� Z ������˳��������������ͬ�㴰��
				if pyRoot in pySubDialogs :
					pySubDialogs.remove( pyRoot )
					pySubDialogs.append( pyRoot )								# ��ָ���Ĵ��ڷŵ���ǰ��
				for pyDlg in pySubDialogs :										# ѭ������ ָ������ �� ĳ�Ӵ��� ���Ӵ���
					zseg = pyDlg.posZSegment
					if zseg not in pyDialogs or pyDlg not in pyDialogs[zseg] : 	# ������Ӵ��ڲ����Ӵ����б���
						stack.push( pyDlg )										# ����ջ
			elif pyTop != pyParent and pyTop.rvisible :							# ���ջ���Ĵ����Ѿ������������Ҳ�����ײ�Ĵ���
				pyDialog = stack.pop()
				zseg = pyDialog.posZSegment
				pyLayerDlgs = pyDialogs.get( zseg, None )
				if pyLayerDlgs :
					pyLayerDlgs.append( pyDialog )								# �򽫸ô��ڳ�ջ����ӵ��Ӵ����б���
				else :
					pyDialogs[zseg] = [pyDialog]
			else :																# ����
				stack.pop()														# ��ջ
		return pyDialogs														# ���ظ�����Ӵ����б�

	def __getRootDialogsTree( self, pyRoot ) :
		"""
		��ȡָ�����ڵ����и����ں��Ӵ����б�
		�����˳���ǣ��ִ��� --> ������
		"""
		pyOwner = pyRoot														# �ҵĸ�����
		while True :															# һֱ������
			if pyOwner.pyOwner is None :										# ׷���ҵ����ϲ㸸����
				break
			pyOwner = pyOwner.pyOwner
		pyDialogs = self.__getSubDialogs( pyOwner, pyRoot )
		zseg = pyOwner.posZSegment
		if zseg in pyDialogs :
			pyDialogs[zseg].append( pyOwner )
		else :
			pyDialogs[zseg] = [pyOwner]
		return pyDialogs														# �������в�θ��Ӵ����б�

	# -------------------------------------------------
	def __addVSRoot( self, pyRoot ) :
		"""
		���һ���ɼ����ڵ��ɼ������б�
		"""
		zseg = pyRoot.posZSegment
		if pyRoot not in self.__pyVSRoots[zseg] :
			self.__pyVSRoots[zseg].append( pyRoot )

	def __removeVSRoot( self, pyRoot ) :
		"""
		�ӿɼ������б���ɾ��һ������
		"""
		zseg = pyRoot.posZSegment
		if pyRoot in self.__pyVSRoots[zseg] :
			self.__pyVSRoots[zseg].remove( pyRoot )

	# -------------------------------------------------
	def __activeTopRoot( self ) :
		"""
		�������Ĵ���
		"""
		pyRoots = self.getVSRoots()					# ��ȡ���пɼ�����
		pyRoot = None
		for pyTmp in pyRoots :						# ˳��
			if pyTmp.activable :					# �ҳ���һ��
				pyRoot = pyTmp						# �ɱ�����Ĵ���
		if pyRoot is not None :						# ����ҵ�
			self.activeRoot( pyRoot, False )		# �򼤻�֮

	# -------------------------------------------------
	def __orderHideRoots( self ) :
		"""
		˳�����ص�ǰ�򿪵Ĵ���
		"""
		for pyRoot in self.getVSRoots() :			# �������пɼ�����
			if pyRoot.escHide :						# ����������� esc ������
				pyRoot.hide()						# �����ش���
				return True							# �������سɹ�
		return False								# �������ز��ɹ�


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		��Ϸ״̬�ı�ǰ������
		"""
		pyRoots = self.getRoots()
		for pyRoot in pyRoots :
			pyRoot.beforeStatusChanged( oldStatus, newStatus )			# ��״̬�ı�֪ͨ���д���

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		��Ϸ״̬�ı�󱻵���
		"""
		pyRoots = self.getRoots()
		for pyRoot in pyRoots :
			pyRoot.afterStatusChanged( oldStatus, newStatus )			# ��״̬�ı�֪ͨ���д���

	def onRoleEnterWorld( self ) :
		"""
		����ɫ��������ʱ������
		"""
		rootDockMgr.onRoleEnterWorld()									# ֪ͨ����ͣ��������

	def onRoleLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ������
		"""
		for pyRoot in self.getRoots() :
			try :
				pyRoot.onLeaveWorld()									# ֪ͨ���д��ڽ�ɫ���뿪����
			except Exception, err :
				EXCEHOOK_MSG( err )
		from guis.ScreenViewer import ScreenViewer
		ScreenViewer().onLeaveWorld()

	def onRoleInitialized( self ) :
		"""
		����ɫ��ʼ�����ʱ������
		"""
		for pyRoot in self.getRoots() :
			pyRoot.onEnterWorld()										# ֪ͨ���д��ڽ�ɫ��ʼ�����
		from guis.ScreenViewer import ScreenViewer
		ScreenViewer().onEnterWorld()

	# ---------------------------------------
	def onRootShow( self, pyRoot ) :
		"""
		����һ��������ʾʱ������
		"""
		uiSounder.initRootSound( pyRoot )
		self.__addVSRoot( pyRoot )
		self.upgradeRoot( pyRoot )
		if pyRoot.activable :
			self.activeRoot( pyRoot, False )

	def onRootHide( self, pyRoot ) :
		"""
		����һ����������ʱ������
		"""
		self.__removeVSRoot( pyRoot )
		if pyRoot == self.getActRoot() :
			self.__activeTopRoot()

	def onZSegmentChanged( self, pyRoot, oldSeg, newSeg ) :
		"""
		���Ĵ������
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
		���һ�����㴰�ڵ�������
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
		�ӹ�������ɾ��һ������
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
		��ȡ�������е����д���
		"""
		pyRoots = []
		for rs in self.__pyRoots.itervalues() :
			pyRoots += rs.list()
		return pyRoots

	def getVSRoots( self ) :
		"""
		��ȡ�����������пɼ��Ĵ���
		"""
		pyVSRoots = []
		for pyRoots in self.__pyVSRoots.values() :
			pyVSRoots += sorted( pyRoots.list(), key = lambda r : r.posZ )
		return pyVSRoots

	def getActRoot( self ) :
		"""
		��ȡ��ǰ������Ĵ���
		"""
		if self.__pyActRoot is None :
			return None
		return self.__pyActRoot()

	def getHitRoot( self, pos ) :
		"""
		��ȡָ�����µ����ϲ��Ǹ� UI
		"""
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.getGui().hitTest( *pos ) :
				return pyRoot
		return None

	def getHitRoots( self, pos ) :
		"""
		��ȡ��ָ������е����пɼ� UI
		"""
		pyRoots = []
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.getGui().hitTest( *pos ) :
				pyRoots.append( pyRoot )
		return pyRoots

	def getMouseHitRoot( self ) :
		"""
		��ȡ��ǰ�������е��������Ǹ�����
		"""
		for pyRoot in self.getVSRoots() :
			if not pyRoot.hitable : continue
			if pyRoot.isMouseHit() : return pyRoot
		return None

	def getMouseHitRoots( self ) :
		"""
		��ȡ�����е����пɼ� UI
		"""
		pyRoots = []
		for pyRoot in self.getVSRoots():
			if not pyRoot.hitable : continue
			if pyRoot.isMouseHit() : pyRoots.append( pyRoot )
		return pyRoots

	# ---------------------------------------
	def isActRoot( self, pyRoot ) :
		"""
		�ж�ָ�������Ƿ��Ǽ����
		"""
		return pyRoot == self.getActRoot()

	def isMouseHitScreen( self ) :
		"""
		�ж�����Ƿ�û�л����κδ���
		"""
		return self.getMouseHitRoot() is None

	# -------------------------------------------------
	def activeRoot( self, pyRoot, upgrade = True ) :
		"""
		����һ�����ڣ��������ɹ��򷵻� True�����򷵻� False
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
		ȡ��һ�����ڵļ���״̬��
		��� pyRoot Ϊ None����ȡ����ǰ����ڵļ���״̬�������� True
		��� pyRoot ��Ϊ None�����жϵ�ǰ����Ĵ����Ƿ���ָ���Ĵ��ڣ�������ǣ��򷵻� False������ȡ�����ļ���״̬������ True
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
		��һ�������ᵽǰ����ʾ
		"""
		def relayout( pyRoots, start, end ) :
			count = len( pyRoots )
			if count == 0 : return
			delta = ( end - start ) / count
			for i, pyTmp in enumerate( pyRoots ) :
				pyTmp.posZ = start + i * delta

		pyRDialogs = self.__getRootDialogsTree( pyRoot )	# ��ȡ���ڵĸ��ӹ�ϵ������
		for zseg, pyDialogs in pyRDialogs.iteritems() :			# �������ɼ� UI �����ֵ
			start, end, act = self.__segRngs[zseg]
			pyVSRoots = self.__pyVSRoots[zseg].list()
			pyVSRoots.sort( key = lambda py : py.posZ )
			relayout( pyVSRoots, start, end )				# ��������ͬ��Ŀɼ����ڵĲ�ι�ϵ
			relayout( pyDialogs, act, start )				# ����������Ҫ��ǰ��ʾ�Ĵ��ڹ�ϵ�б�
		GUI.reSort()
		GUI.reSortFocusList( pyRoot.getGui() )

	def upgradeMouseHitRoot( self ) :
		"""
		����ǰ�����еĴ����ᵽǰ����ʾ
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
