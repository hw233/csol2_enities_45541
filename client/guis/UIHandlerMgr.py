# -*- coding: gb18030 -*-
#
# $Id: UIHandlerMgr.py,v 1.20 2008-08-02 09:28:18 huangyongwei Exp $

"""
implement ui global event handlers
2005/10/27 : wirten by huangyongwei
"""

import weakref
import csol
import GUI
import IME
import guis.util as util
from bwdebug import *
from AbstractTemplates import Singleton
from Weaker import WeakList
from Function import Functor
from keys import *
from gbref import rds
from guis.RootUIsMgr import ruisMgr
from ExtraEvents import LastMouseEvent
from ExtraEvents import LastKeyDownEvent
from ExtraEvents import LastKeyUpEvent
from guis.common.ScriptObject import ScriptObject


# --------------------------------------------------------------------
# implement cap ui handler
# --------------------------------------------------------------------
class CapHandler :
	"""
	������ȼ��� UI ��Ϣ������
	"""
	def __init__( self ) :
		self.__pyCapUI = None						# ���汻 cap �� UI

		self.__isMouseInCapUI = False				# ��ʱ�������������Ƿ��� UI ����

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		pyCapUI = self.getCapUI()									# ��ȡ�� cap �� UI
		if pyCapUI is None : return False							# ���û�б� cap �� UI���򲻴�����Ϣ����
		if not pyCapUI.rvisible or not pyCapUI.enable :				# �жϱ� cap �� UI �Ƿ�ɼ�������
			self.uncapUI()											# ������ɼ���Ҳ�����ã���ȡ�� cap
			return False											# ��������Ϣ����
		if key in KEY_MOUSE_KEYS :									# �������������
			if not pyCapUI.focus : return False						# ��������갴����Ϣ�������
			pyCapUI.handleMouseButtonEvent( pyCapUI.getGui(), \
				key, down, mods, csol.rcursorPosition() )			# ���������Ϣ
		elif pyCapUI.focus : 										# ������ܼ�����Ϣ
			pyCapUI.handleKeyEvent( down, key, mods )				# ���ͼ�����Ϣ
		return True													# ���Ƿ��� True��������Ϣ���·�

	# ---------------------------------------
	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		pyCapUI = self.getCapUI()										# ��ȡ�� cap �� UI
		if pyCapUI is None : return False								# ���û�б� cap �� UI
		if not pyCapUI.rvisible :										# �жϱ� cap �� UI �Ƿ�ɼ�
			self.uncapUI()												# ������ɼ���Ҳ�����ã���ȡ�� cap
			return False												# ��������Ϣ����
		pos = csol.rcursorPosition()									# ������Ļλ��
		isMouseHit = pyCapUI.isMouseHit()								# ����Ƿ��� UI ����
		if pyCapUI.crossFocus :											# ��������������¼�
			if isMouseHit and not self.__isMouseInCapUI :				# �������� UI ���ϣ�����ʱ������Ϊ True
				pyCapUI.handleMouseEnterEvent( pyCapUI.getGui(), pos )	# �򴥷��������¼�
				self.__isMouseInCapUI = True							# ������ʱ��������Ϊ True
			elif not isMouseHit and self.__isMouseInCapUI :				# �����겻�� UI���ϣ�����ʱ����Ϊ False
				pyCapUI.handleMouseLeaveEvent( pyCapUI.getGui(), pos )	# �򴥷�����뿪�¼�
				self.__isMouseInCapUI = False							# ����ʱ��������Ϊ False
		if pyCapUI.moveFocus :											# ��������ƶ���Ϣ
			pyCapUI.handleMouseEvent( pyCapUI.getGui(), pos )			# �򴥷�����ƶ���Ϣ
		else :															# ��������������Ϣ
			return False
		return True														# ������������ƶ���Ϣ

	# -------------------------------------------------
	def getCapUI( self ) :
		"""
		��ȡ��ǰ�� cap �� UI�����û�б� cap �� UI���򷵻� None
		"""
		if self.__pyCapUI is None :
			return None
		pyCapUI = self.__pyCapUI()
		if not pyCapUI or pyCapUI.disposed :
			self.__pyCapUI = None
			return None
		return pyCapUI

	def capUI( self, pyUI ) :
		"""
		cap һ�� UI
		"""
		assert pyUI is not None											# ����Ϊ None
		pyCapUI = self.getCapUI()										# ��ȡ��ǰ�� cap �� UI
		if pyCapUI is None :											# �����ǰû�б� cap �� UI
			self.__pyCapUI = weakref.ref( pyUI )						# �� cap ָ�� UI
		else :															# ����û���ͷž� UI ֮ǰ
			del pyCapUI
			ERROR_MSG( "the foregoing caped ui is not released!" )		# ������ cap �µ� UI

	def uncapUI( self, pyUI = None ) :
		"""
		�ͷ�һ���� cap �� UI����� ָ���� UI Ϊ None����ȡ����ǰ�� cap ��UI
		"""
		if pyUI is None or self.getCapUI() == pyUI :
			self.__pyCapUI = None


# --------------------------------------------------------------------
# implement active ui handler
# --------------------------------------------------------------------
class TabInHandler :
	"""
	��ý���� UI ��Ϣ������( ��Ҫ�����ı����� )
	"""
	def __init__( self ) :
		self.__pyTabInUI = None										# ���浱ǰӵ�н���� UI

	# --------------------------------------------------------------------
	# public
	# --------------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		if key in KEY_MOUSE_KEYS : return False						# ��������갴����Ϣ
		pyUI = self.getTabInUI()									# ��ȡ��ǰӵ�н���� UI
		if pyUI is None : return False								# ���û�н��� UI���򷵻�
		pyActRoot = ruisMgr.getActRoot()							# ��ü����
		if pyActRoot and pyActRoot != pyUI.pyTopParent :			# �������ؼ������Ĵ���û�б�����
			return False											# �򲻴�����Ϣ����

		if not pyUI.rvisible or not pyUI.enable :					# �����ǰ���� UI ��Ч���򲻿ɼ�
			self.tabOutUI()											# ��ȡ�����Ľ���
		elif pyUI.handleKeyEvent( down, key, mods ) :				# ������� UI �����˰�����Ϣ
			return True												# ���۶���Ϣ
		return False												# ��������Ϣ�������·�

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		return False												# ���� UI ����������ƶ���Ϣ

	# -------------------------------------------------
	def getTabInUI( self ) :
		"""
		��ȡ��ǰӵ�н���� UI
		"""
		if self.__pyTabInUI is None :
			return None
		pyUI = self.__pyTabInUI()
		if pyUI is None : return None
		if not pyUI.rvisible or not pyUI.enable :
			self.tabOutUI()
			return None
		return pyUI

	def tabInUI( self, pyUI ) :
		"""
		��ָ�� UI ��ý���
		"""
		if not pyUI.rvisible : return False			# ��ý���� UI ����ɼ�
		if not pyUI.enable : return False			# ��ý���� UI �������
		pyTopParent = pyUI.pyTopParent
		if pyTopParent is None : return False
		if not pyTopParent.activable : return False	# ���������ڲ��ɱ�����

		pyTabInUI = self.getTabInUI()				# ��õ�ǰ���� UI
		if pyUI == pyTabInUI : return False			# �Ѿ�ӵ�н��㣬�򷵻�
		if pyTabInUI is not None :					# �����ǰ��ӵ�н���� UI
			self.__pyTabInUI = None					# ȡ��֮ǰ���� UI �Ľ��㣬�򣬽�ԭ���� UI �Ľ���ȡ��
			pyTabInUI.onTabOut_()					# �����������뽹��Ϣ������������ı����������ǲ��õ���ƣ�
		ruisMgr.activeRoot( pyUI.pyTopParent )		# ��ý���� UI �Ķ��㴰�ڣ������Ϊ��ǰ� UI
		self.__pyTabInUI = weakref.ref( pyUI )		# ������ UI ����Ϊָ���� UI
		pyUI.onTabIn_()								# ���������� tab in ��Ϣ������������ı����������ǲ��õ���ƣ�
		return True									# �������óɹ�

	def tabOutUI( self, pyUI = None ) :
		"""
		ȡ��ָ���Ľ��� UI �Ľ��㣬���û��ָ�� UI����ȡ����ǰ���� UI �Ľ���
		"""
		pyTabInUI = None
		if self.__pyTabInUI :
			pyTabInUI = self.__pyTabInUI()			# ��ȡ��ǰ���� UI
		if pyTabInUI is None : return False			# �����ǰû�н��� UI���򷵻�ȡ��ʧ��
		if pyUI is None or pyUI == pyTabInUI :		# ���ָ���� UI Ϊ None ��ָ�� UI ���ǽ��� UI
			self.__pyTabInUI = None					# ��ȡ������ UI �Ľ���
			pyTabInUI.onTabOut_()					# �����������뽹��Ϣ������������ı����������ǲ��õ���ƣ�
			return True								# ���س�������ɹ�
		return False								# ���س���ʧ��


# --------------------------------------------------------------------
# implement active ui handler
# --------------------------------------------------------------------
class ActHandler :
	"""
	��ǰ����ڵ���Ϣ������
	"""
	def __init__( self ) :
		pass

	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		if key in KEY_MOUSE_KEYS : return False					# ������������Ϣ
		pyActUI = ruisMgr.getActRoot()							# ��ȡ��ǰ����� ����
		if pyActUI is None : return False						# ���û�м����
		if not pyActUI.enable :									# ���������Ĵ��ڲ����ã������������������ڣ�
			return False										# �򲻴�����Ϣ����
		if pyActUI.handleKeyEvent( down, key, mods ) :			# �������̰�����Ϣ
			return True											# �������ڴ�������Щ��Ϣ���򷵻� True
		return False											# ���򷵻� False

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		return False											# ����ڲ���������ƶ���Ϣ


# --------------------------------------------------------------------
# implement shield ui handler
# --------------------------------------------------------------------
class ShieldHandler :
	"""
	ȫ��������Ϣ UI ��Ϣ������
	"""
	def __init__( self ) :
		self.__pyShieldUIs = WeakList()							# ��ǰ�� shield �� UI �б�
		self.__pyLastHitedUIs = WeakList()						# ��ʱ������������������ϵ� UI �б����ڴ��������롢�뿪��Ϣ��


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getSubHitUIs( self, pyShieldUI ) :
		"""
		��ȡָ�� UI �����б������е��� UI
		"""
		shieldUI = pyShieldUI.getGui()									# ��ȡ���� UI
		def verifier( pyUI ) :											# ��֤����
			if not pyUI.rvisible : return False, 0						# ���ɼ������ټ������� UI
			if not pyUI.isMouseHit() : return False, 0					# ���û�л��У����ټ������� UI
			if not pyUI.acceptEvent : return False, 1					# ��������Ϣ
			if not pyUI.enable : return False, 0						# ������ã����ټ������� UI
			return True, 1
		return util.postFindPyGui( shieldUI, verifier, True )			# ��ȡ���б������е� UI

	# ---------------------------------------
	def __dsbMouseButtonEvent( self, pyShieldUI, down, key, mods ) :
		"""
		�ַ���갴����Ϣ
		"""
		pySubUIs = self.__getSubHitUIs( pyShieldUI )					# ��ȡ������ UI
		for pySubUI in pySubUIs :										# ˳��ַ���Ϣ
			if not pySubUI.focus : continue								# �� UI ��������갴����Ϣ������Ϣ�ύ����һ��
			if pySubUI.handleMouseButtonEvent( pySubUI.getGui(), \
				key, down, mods, csol.rcursorPosition() ) :				# ����� UI ������갴����Ϣ���򴥷����İ�����Ϣ
					return True											# ������Ϣ����
		return False													# ���û���� UI ���������Ϣ���򣬽���������Ϣ

	def __dsbKeyEvent( self, pyShieldUI, down, key, mods ) :
		"""
		�ַ�������Ϣ
		"""
		return True														# ���ص����м�����Ϣ


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		pyShieldUI = self.getShieldUI()											# ��ȡ shield UI
		if pyShieldUI is None : return False									# ��� shield UI ������
		if not pyShieldUI.rvisible :											# �����ǰ�� shield �� UI ���ɼ�
			self.clearShieldUI( pyShieldUI )									# ����� shield �б������
			return self.handleKeyEvent( down, key, mods )						# ������Ϣ������һ�� shield UI
		elif not pyShieldUI.enable :											# ��� UI ��Ч�������������û�У�
			return True															# �򷵻���Ϣ�Ѿ�����
		if key in KEY_MOUSE_KEYS :												# ����Ǽ��̰���
			return self.__dsbMouseButtonEvent( pyShieldUI, down, key, mods )	# �ַ���갴����Ϣ
		elif self.__dsbKeyEvent( pyShieldUI, down, key, mods ) :				# �ַ����̰�����Ϣ
			return True
		return False															# �����������������Ϣ��������Զ����ִ��

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		pyShieldUI = self.getShieldUI()												# ��ȡ shield UI
		if pyShieldUI is None : return False										# ���û�� shield UI���򲻴�����
		pySubUIs = self.__getSubHitUIs( pyShieldUI )								# ��ȡ�����е��� UI
		pyNewHitUIs = [u for u in pySubUIs if u not in self.__pyLastHitedUIs]		# �����У���������ʱ�б��е��� UI
		pyOldHitUIs = [u for u in self.__pyLastHitedUIs if u not in pySubUIs]		# ���û�л��У�������ʱ�б��е� UI
		for pyUI in pyNewHitUIs :													# ��������
			pyUI.handleMouseEnterEvent( pyUI.getGui(), csol.rcursorPosition() )		# ���ոջ��е��� UI ���������¼�
		for pyUI in pyOldHitUIs :													# ��������
			pyUI.handleMouseLeaveEvent( pyUI.getGui(), csol.rcursorPosition() )		# ���ո��뿪���� UI ������뿪�¼�
		self.__pyLastHitedUIs.clear()												# �����ʱ�б�
		self.__pyLastHitedUIs.appends( pySubUIs )									# ���¶���ʱ�б�ֵ

		for pySubUI in pySubUIs :														# �����б������е��� UI
			if pySubUI.handleMouseEvent( pySubUI.getGui(), csol.rcursorPosition() ) :	# ������������ƶ��¼�
				break																	# �����Ϣ����������򲻼������·�
		return True																		# ���ص���������ƶ��¼�

	# -------------------------------------------------
	def getShieldUI( self ) :
		"""
		��ȡ��ǰ������Ϣ�� UI
		"""
		if len( self.__pyShieldUIs ) :
			return self.__pyShieldUIs[-1]
		return None

	def setShieldUI( self, pyUI ) :
		"""
		���õ�ǰ������Ϣ�� UI
		"""
		if pyUI in self.__pyShieldUIs :
			self.__pyShieldUIs.remove( pyUI )
		self.__pyShieldUIs.append( pyUI )
		self.__pyLastHitedUIs.clear()

	def clearShieldUI( self, pyUI = None ) :
		"""
		���ָ��������Ϣ�� UI�����ָ���� UI Ϊ None����ɾ����ǰ������Ϣ�� UI
		"""
		if pyUI is None :
			self.__pyShieldUIs.clear()
		elif pyUI in self.__pyShieldUIs :
			self.__pyShieldUIs.remove( pyUI )
		self.__pyLastHitedUIs.clear()


# --------------------------------------------------------------------
# implement cast ui handler
# --------------------------------------------------------------------
class CastHandler :
	"""
	cast UI ����Ϣ��������cast UI һ�����ڲ˵��б��һЩ�����������б�
	"""
	def __init__( self ) :
		self.__pyCastUIs = WeakList()						# cast UI �б�

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		pyCastUI = self.getCastUI()										# ��ȡ��ǰ�� cast �� UI
		if pyCastUI is None : return False								# ��ǰû�б� cast �� UI
		if key in KEY_MOUSE_KEYS :										# �������갴����Ϣ
			if pyCastUI.handleMouseButtonEvent( pyCastUI.getGui(), \
				key, down, mods, csol.rcursorPosition() ) :				# ��������Ϣ�� cast UI ����
					return True											# ���ص�
			return False												# ����Ϣ����
		else :
			pyCastUI.handleKeyEvent( down, key, mods )					# ���ͼ��̰�����Ϣ
		return True														# �����������ؼ�����Ϣ

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		return False													# ����������������ƶ���Ϣ

	# -------------------------------------------------
	def getCastUI( self ) :
		"""
		��ȡ��ǰ�� cast �� UI
		"""
		count = len( self.__pyCastUIs )
		for idx in xrange( count - 1, -1, -1 ) :
			pyUI = self.__pyCastUIs[idx]
			if not pyUI.rvisible : continue
			if not pyUI.enable : continue
			return pyUI
		return None

	def castUI( self, pyUI ) :
		"""
		���� cast UI
		"""
		assert pyUI is not None, "you can't cast a none ui!"
		if pyUI in self.__pyCastUIs :
			self.__pyCastUIs.remove( pyUI )
		self.__pyCastUIs.append( pyUI )

	def uncastUI( self, pyUI = None ) :
		"""
		ȡ��ָ�� UI �� cast ���ȼ������ָ�� UI Ϊ None����ȡ����ǰ�� cast �� UI
		"""
		if pyUI is None :
			self.__pyCastUIs.clear()
		elif pyUI in self.__pyCastUIs :
			self.__pyCastUIs.remove( pyUI )


# --------------------------------------------------------------------
# implement common ui handler
# --------------------------------------------------------------------
class CommonHandler :
	"""
	��ͨ UI ��Ϣ������
	"""
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		��������Ϣ
		"""
		if key not in KEY_MOUSE_KEYS : return False					# ��������̰�����Ϣ
		return GUI.handleKeyEvent( down, key, mods ) 				# ����갴����Ϣ�������洦��

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		return GUI.handleMouseEvent( dx, dy, dz )					# ������ƶ��¼��������洦��


# --------------------------------------------------------------------
# handlerMgr
# --------------------------------------------------------------------
class UIHandlerMgr( Singleton ) :
	"""
	��Ϣ������
	"""
	def __init__( self ) :
		self.__capHandler = CapHandler()							# cap UI�������Ϣ���ȼ��� UI����Ϣ������
		self.__tabInHandler = TabInHandler()						# ��ǰӵ�н��� UI ����Ϣ������
		self.__actHandler = ActHandler()							# ��ǰ������� UI ����Ϣ������
		self.__shieldHandler = ShieldHandler()						# ����ȫ����Ϣ�� UI ����Ϣ������
		self.__castHandler = CastHandler()							# cast UI ����Ϣ�����������ȼ���������ͨ UI��
		self.__commonHandler = CommonHandler()						# ��ͨ UI ����Ϣ������

		self.__cycleKey = 0											# ��ʱ��������¼���һ�α����µ���갴��
		self.__cycleKeyCBID = 0										# �������� ��ʱ�䰴�°��� ����Ϣ callback ID
		self.__tmpMousePos = ( 0, 0 )								# ��¼���λ��
		self.mouseOffset = ( 0, 0 )									# ���ÿ���ƶ� tick �Ĳ�ֵ


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __handleMouseScroll( self, dz ) :
		"""
		������������Ϣ
		"""
		def verifier( pyUI ) :
			if not pyUI.rvisible : return False, 0						# ������� UI ���ɼ������ټ����� UI ���� UI
			if not pyUI.isMouseHit() : return False, 0					# ������û���и��� UI�����ټ����� UI ���� UI
			if getattr( pyUI, "mouseScrollFocus", False ) :				# �ж��ͷŽ��չ����¼�
				return True, 1											# ������� UI ���Խ��ܹ����¼�������ӵ��б��У������������� UI
			return False, 1												# ������� UI ��������������Ϣ������Ը��� UI������������������ UI

		pyRoot = ruisMgr.getMouseHitRoot()								# ��ȡ�����еĴ���
		if pyRoot is None : return False								# ���û�л��еĴ����򷵻�
		pyChs = util.postFindPyGui( pyRoot.getGui(), verifier, True )	# �� Z ����˳���ҳ������� UI
		for pyCh in pyChs :
			res = pyCh.onMouseScroll_( dz )								# ������ UI �Ĺ�����Ϣ��������� UI �ı�����������Ʋ��ã�
			if res is None :
				raise TypeError( "method '%s' must return a bool!" % \
					str( pyCh.onMouseScroll_ ) )
			if res :
				return True
		return False													# û�д��������Ϣ���� UI

	# -------------------------------------------------
	def __dsbKeyEvent( self, down, key, mods ) :
		"""
		˳��ַ������¼�
		"""
		if self.__capHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__tabInHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__actHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__shieldHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__castHandler.handleKeyEvent( down, key, mods ) :
			return True
		elif self.__commonHandler.handleKeyEvent( down, key, mods ) :
			return True
		return False

	def __cycleKeyDown( self, down, key, mods ) :
		"""
		ѭ��������갴����Ϣ
		"""
		self.__dsbKeyEvent( down, key, mods )							# �ַ���Ϣ
		#if not BigWorld.isKeyDown( self.__cycleKey ) : return			# �����Ѿ�����
		self.__cycleKeyCBID = BigWorld.callback( 0.1, \
			Functor( self.__cycleKeyDown, down, key, mods ) )			# ѭ������

	def __rehandleKeyEvent( self, down, key, mods ) :
		"""
		�ظ���������Ϣ
		"""
		if key in KEY_MOUSE_KEYS :										# �������갴����Ϣ
			return self.__dsbKeyEvent( down, key, mods )				# ��ַ���갴����Ϣ
		elif down or key == self.__cycleKey :							# ������¼��̼�
			BigWorld.cancelCallback( self.__cycleKeyCBID )				# ��ֹ֮ͣǰ��ѭ����������
		
		if IME.is9FangInputActivated(): 								# 9�����뷨����
			if key in KEY_9FANGINPUT_HOOK_KEYS:							# ����9�����뷨���̲���ļ�ֵ
				return True
			if down and key == KEY_W and not csol.isVirtualKeyDown( 0x57 ):	# ����9�����뷨ѡȡ��ʱ������DXInput���Ͷ����w��ֵ��Bug
				return True
		
		if down :														# ����ǰ��¼�
			self.__cycleKey = key										# �򣬼�¼���µļ�
			if key not in KEY_MODIFIER_KEYS and not IME.isActivated() :	# ���ð��¸��Ӽ������ظ�( ע�⣺IME ����ʱ���ظ���
																		# ԭ���� IME �� bug������û���ؼ��̰�����Ϣ���������˼���������Ϣ��
																		# ��ˣ�������ų� IME �������� callback ��ͣ����)
				self.__cycleKeyCBID = BigWorld.callback( 0.3, \
					Functor( self.__cycleKeyDown, down, key, mods ) )	# �������ģ����������
		return self.__dsbKeyEvent( down, key, mods )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCapUI( self ) :
		"""
		��ȡ�� cap �� UI
		"""
		return self.__capHandler.getCapUI()

	def capUI( self, pyUI ) :
		"""
		���� cap �� UI
		"""
		self.__capHandler.capUI( pyUI )

	def uncapUI( self, pyUI = None ) :
		"""
		ȡ��ָ�� UI �� cap�����ָ�� UI Ϊ None����ȡ����ǰ�� cap �� UI
		"""
		return self.__capHandler.uncapUI( pyUI )

	def isCapped( self, pyUI ) :
		"""
		�ж�ĳ�� UI �Ƿ��Ǳ� cap �� UI
		"""
		return self.__capHandler.getCapUI() == pyUI

	# -------------------------------------------------
	def getTabInUI( self ) :
		"""
		��ȡ��ǰ��ý���� UI
		"""
		return self.__tabInHandler.getTabInUI()

	def tabInUI( self, pyUI ) :
		"""
		����ĳ�� UI ӵ�н���
		"""
		return self.__tabInHandler.tabInUI( pyUI )

	def tabOutUI( self, pyUI = None ) :
		"""
		ȡ��ָ�� UI �Ľ��㣬���ָ�� UI Ϊ None����ȡ����ǰӵ�н���� UI
		"""
		return self.__tabInHandler.tabOutUI( pyUI )

	def isTabInUI( self, pyUI ) :
		"""
		�жϵ�ǰӵ�н���� UI �Ƿ���ָ�� UI
		"""
		return self.__tabInHandler.getTabInUI() == pyUI

	# -------------------------------------------------
	def getShieldUI( self ) :
		"""
		��ȡ��ǰ��� Shield UI
		"""
		return self.__shieldHandler.getShieldUI()

	def setShieldUI( self, pyUI ) :
		"""
		����ָ�� UI Ϊ��ǰ��� shield UI
		"""
		return self.__shieldHandler.setShieldUI( pyUI )

	def clearShieldUI( self, pyUI ) :
		"""
		�� shield �б������һ�� shield UI
		"""
		self.__shieldHandler.clearShieldUI( pyUI )

	def isShieldUI( self, pyUI ) :
		"""
		�ж�ָ�� UI �Ƿ��ǵ�ǰ����� shield UI
		"""
		return self.__shieldHandler.getShieldUI() == pyUI

	# -------------------------------------------------
	def getCastUI( self ) :
		"""
		��ȡ��ǰ�� cast �� UI
		"""
		return self.__castHandler.getCastUI()

	def castUI( self, pyUI ) :
		"""
		cast ָ�� UI
		"""
		self.__castHandler.castUI( pyUI )

	def uncastUI( self, pyUI = None ) :
		"""
		ȡ��ָ�� UI �� cast�����ָ�� UI Ϊ None����ȡ����ǰ�� cast ��UI
		"""
		self.__castHandler.uncastUI( pyUI )

	def isCasted( self, pyUI ) :
		"""
		�жϵ�ǰ cast �� UI �Ƿ���ָ���� UI
		"""
		return self.__castHandler.getCastUI() == pyUI


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRootInactivated( self, pyRoot ) :
		"""
		��ĳ�����ڱ�����ʱ����
		"""
		self.tabOutUI()


	# ----------------------------------------------------------------
	# global handlers
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		�������¼�
		"""
		result = rds.ruisMgr.dragObj.dragging
		if down and key == KEY_LEFTMOUSE :							# �������������
			if not ruisMgr.upgradeMouseHitRoot() :					# �������е� UI �ᵽ��ǰ��
				ruisMgr.inactiveRoot()								# ȡ����ǰ������ڵļ���״̬

		if self.__rehandleKeyEvent( down, key, mods ) :				# �ַ�������Ϣ
			result = True											# �����Ϣ���ػ�

		if down : LastKeyDownEvent.notify( key, mods )				# ֪ͨ���������¼�
		else:
			if key == KEY_LEFTMOUSE: 
				pyRoot = ruisMgr.getMouseHitRoot()
				if not result and pyRoot and pyRoot.hitable:
					if rds.worldCamHandler.fixed() :
						rds.worldCamHandler.unfix()
					result = True
			LastKeyUpEvent.notify( key, mods )					# ֪ͨ�����������¼�
		return result

	# ---------------------------------------
	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		��������ƶ���Ϣ
		"""
		newX, newY = csol.pcursorPosition()
		oldX, oldY = self.__tmpMousePos
		dx, dy = newX - oldX, newY - oldY							# ע�⣺����� dx��dy ������
		self.mouseOffset = dx, dy
		self.__tmpMousePos = newX, newY

		# -----------------------------------
		if dz != 0 and self.__handleMouseScroll( dz ) :				# �����������¼�
			rds.ccursor.normal()									# �����ָ��Ϊ��ͨ״̬����ֹ����뿪�����Ӳ���ԭ�������������ƺ�������ʣ���
			result = True

		# -----------------------------------
		result = False
		if self.__capHandler.handleMouseEvent( dx, dy, dz ) :		# �� cap UI ��������ƶ���Ϣ
			result = True
		elif self.__tabInHandler.handleMouseEvent( dx, dy, dz ) :	# �ý��� UI �������Ӧ��Ϣ
			result = True
		elif self.__actHandler.handleMouseEvent( dx, dy, dz ) :		# �ü���ڴ�������ƶ���Ϣ
			result = True
		elif self.__shieldHandler.handleMouseEvent( dx, dy, dz ) :	# �� shield UI ��������ƶ���Ϣ
			result = True
		elif self.__castHandler.handleMouseEvent( dx, dy, dz ) :	# �� cast UI ��������ƶ���Ϣ
			result = True
		elif self.__commonHandler.handleMouseEvent( dx, dy, dz ) :	# ��ͨ UI ��������ƶ���Ϣ
			result = True

		# -----------------------------------
		LastMouseEvent.notify( dx, dy, dz )							# ����ƶ������Ϣ

		# -----------------------------------
		return result

	def resetMouseState( self ):
		rds.worldCamHandler.unfix()
	
	def onEnterUIArea( self, pyRoot, down, key ):
		pass
		
	def onLeaveUIArea( self, pyRoot, down, key ):
		pass


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
uiHandlerMgr = UIHandlerMgr()
