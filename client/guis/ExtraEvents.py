# -*- coding: gb18030 -*-
#
# $Id: ExtraEvents.py,v 1.29 2008-06-23 06:13:20 huangyongwei Exp $

"""
implement ui events are not contained by engine
-- 2006/06/10 : writen by huangyongwei
"""

import sys
import weakref
import BigWorld
import Function
import guis.Debug as Debug
from Weaker import WeakList
from bwdebug import *

# --------------------------------------------------------------------
# implement control events manager
# --------------------------------------------------------------------
class ControlEvent( object ) :
	"""
	�¼���( ע�⣺�󶨵ķ���һ����ʵ������ )
	"""
	__slots__ = (
		"__ownerName",
		"__eventName",
		"__pyWeakUI",
		"__methods",
		"__shield",
		)
	def __init__( self, eventName, pyUI ) :
		self.__ownerName = "%s<%i>" % ( pyUI.__class__.__name__, id( pyUI ) )		# �����ؼ�����
		self.__eventName = eventName												# �¼�����
		self.__pyWeakUI = weakref.ref( pyUI )										# �¼������Ŀؼ�
		self.__methods = WeakList()													# ���������¼�����
		self.__shield = False														# �Ƿ������¼��ַ�

	def __del__( self ) :
		if Debug.output_del_ControlEvent :
			INFO_MSG( "event %s of %s has been delete!" % ( self.__eventName, self.__ownerName ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def isShield( self ) :
		"""
		ָ���¼��Ƿ�������״̬
		"""
		return self.__shield


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __call__( self, *args ) :
		"""
		���������¼�
		"""
		if self.__shield : return True
		res = False
		for method in self.__methods :
			try :
				res = self.__trigger( method, args ) or res
			except :
				EXCEHOOK_MSG( str( method ) )
		return res

	def __repr__( self ) :
		return "(%s, instance of ControlEvent at %#0X)" % ( self.__eventName, id( self ) )

	def __str__( self ) :
		return self.__repr__()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __trigger( self, method, args ) :
		"""
		����һ���¼�
		"""
		count = method.func_code.co_argcount - 1					# ��ȡ�󶨷����Ĳ��������������� 'self' ��
		realCount = len( args )										# ����ʱ�Ĳ������������¼�ʵ��Ӧ�þ߱��Ĳ���������
		if count == realCount :										# ��������Ĳ�����ʵ�ʲ���һ��
			return method( *args )									# ��ֱ�ӵ���
		elif count == realCount + 1 :								# ����󶨷����Ĳ�����ʵ�ʲ����� 1
			pyUI = self.__pyWeakUI()								# ����ζ�Ű󶨷���Ҫ���¼������Ŀؼ���Ϊ��һ���������ݹ�ȥ
			if pyUI is None :										# ����¼������Ŀؼ��Ѿ�������
				raise "%s hasbeen disposed!" % self.__ownerName		# ���׳�����
			return method( pyUI, *args )
		else :
			msg = "the number of arguments are not match!\n"
			msg += "callable object '%s' must contains %d or %d arguments" % ( str( method ), realCount, realCount + 1 )
			raise TypeError( msg )

	# -------------------------------------------------
	def __verify( self, method ) :
		"""
		��֤�Ƿ��ǺϷ��İ��¼�����
		"""
		fname = Function.getMethodName( method )
		if not callable( method ) :
			ERROR_MSG( "event method '%s' is uncallable!" % fname )
			return False
		if method in self.__methods :
			cname = getattr( method, "im_self", None )
			if cname is None :
				cname = getattr( method, "im_class", None )
			WARNING_MSG( "method '%s' of %s has been in the event array!" % ( fname, str( cname ) ) )
			return False
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getEvents( self ) :
		"""
		��ȡ���е��¼�����
		"""
		return self.__methods.list()

	def getEventName( self ) :
		"""
		��ȡ�¼�����
		"""
		return self.__eventName

	def count( self ) :
		"""
		��ȡ�¼�������������
		"""
		return len( self.__methods )

	# -------------------------------------------------
	def bind( self, method, add = False ) :
		"""
		��һ���¼�����
		@type				method : class method
		@param				method : ��ĳ�Ա����
		@type				add	   : bool
		@param				add	   : ���Ϊ True������԰�һ����ʵ���еĶ�������������ٴΰ󶨵�ʱ��ǰһ�ΰ󶨵�ͬһ�෽�����ᱻ����
		"""
		if not self.__verify( method ) : return				# ��֤�¼������ͷźϷ�
		cls = getattr( method, "im_class", None )			# �Ƿ���ʵ������
		if not add : self.removeClassEvents( cls )			# �����������ʵ��������ͬһ���������ԭ���ķ���
		self.__methods.append( method )
		pyUI = self.__pyWeakUI()
		if hasattr( pyUI, 'onEventBinded' ) :				# ���¼���ʱ֪ͨ�����ؼ�
			pyUI.onEventBinded( self.__eventName, method )

	def unbind( self, method ) :
		"""
		�����һ���¼�����
		@type				method : class method
		@param				method : ��ĳ�Ա����
		"""
		if method in self.__methods :
			self.__methods.remove( method )
		pyUI = self.__pyWeakUI()
		if hasattr( pyUI, 'onEventUnbinded' ) :				# ���¼�ȡ����ʱ֪ͨ�����ؼ�
			pyUI.onEventUnbinded( self.__eventName, method )

	# ---------------------------------------
	def removeClassEvents( self, cls ) :
		"""
		�������ָ��ĳ�����Ա�������¼�����
		@type				cls : class
		@param				cls : �ࣨ������������ʵ�����б��󶨵ķ�����
		"""
		for method in self.__methods :
			if not hasattr( method, "im_class" ) :			# ������Ƿ���
				continue									# ����
			if method.im_class is cls :						# �����������ʵ��������ָ������һ��
				self.__methods.remove( method )				# ��ɾ������

	def clear( self ) :
		"""
		������а󶨵��¼�����
		"""
		self.__methods.clear()

	# -------------------------------------------------
	def shield( self ) :
		"""
		���ε��¼��Ĵ���
		"""
		self.__shield = True

	def unshield( self ) :
		"""
		ȡ���¼���������
		"""
		self.__shield = False


# --------------------------------------------------------------------
# galobal mouse move event
# --------------------------------------------------------------------
class LastMouseEvent :
	__cg_events = WeakList()
	__cg_locked = False

	@classmethod
	def attach( SELF, handler ) :
		if handler not in SELF.__cg_events :
			SELF.__cg_events.append( handler )
			return True
		return False

	@classmethod
	def detach( SELF, handler ) :
		if handler in SELF.__cg_events :
			SELF.__cg_events.remove( handler )
			return True
		return False

	@classmethod
	def notify( SELF, dx, dy, dz ) :
		if SELF.__cg_locked : return
		for handler in SELF.__cg_events :
			try :
				handler( dx, dy, dz )
			except :
				EXCEHOOK_MSG()

	@classmethod
	def lock( SELF ) :
		SELF.__cg_locked = True

	@classmethod
	def unlock( SELF ) :
		SELF.__cg_locked = False


# --------------------------------------------------------------------
# after a a key has been held down, the events will be implemented
# --------------------------------------------------------------------
class LastKeyDownEvent :
	__cg_events = WeakList()
	__cg_locked = False

	@classmethod
	def attach( SELF, handler ) :
		if handler not in SELF.__cg_events :
			SELF.__cg_events.append( handler )
			return True
		return False

	@classmethod
	def detach( SELF, handler ) :
		if handler in SELF.__cg_events :
			SELF.__cg_events.remove( handler )
			return True
		return False

	@classmethod
	def notify( SELF, key, mods ) :
		if SELF.__cg_locked : return False
		result = False
		for handler in SELF.__cg_events :
			try :
				result = handler( key, mods ) or result
			except :
				EXCEHOOK_MSG()
		return result

	@classmethod
	def lock( SELF ) :
		SELF.__cg_locked = True

	@classmethod
	def unlock( SELF ) :
		SELF.__cg_locked = False


# --------------------------------------------------------------------
# after a a key has been release, the events will be implemented
# --------------------------------------------------------------------
class LastKeyUpEvent :
	__cg_events = WeakList()
	__cg_locked = False

	@classmethod
	def attach( SELF, handler ) :
		if handler not in SELF.__cg_events :
			SELF.__cg_events.append( handler )
			return True
		return False

	@classmethod
	def detach( SELF, handler ) :
		if handler in SELF.__cg_events :
			SELF.__cg_events.remove( handler )
			return True
		return False

	@classmethod
	def notify( SELF, key, mods ) :
		if SELF.__cg_locked : return False
		result = False
		for handler in SELF.__cg_events :
			try :
				result = handler( key, mods ) or result
			except :
				EXCEHOOK_MSG()
		return result

	@classmethod
	def lock( SELF ) :
		SELF.__cg_locked = True

	@classmethod
	def unlock( SELF ) :
		SELF.__cg_locked = False
