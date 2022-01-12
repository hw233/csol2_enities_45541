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
	事件类( 注意：绑定的方法一定是实例方法 )
	"""
	__slots__ = (
		"__ownerName",
		"__eventName",
		"__pyWeakUI",
		"__methods",
		"__shield",
		)
	def __init__( self, eventName, pyUI ) :
		self.__ownerName = "%s<%i>" % ( pyUI.__class__.__name__, id( pyUI ) )		# 所属控件名称
		self.__eventName = eventName												# 事件名称
		self.__pyWeakUI = weakref.ref( pyUI )										# 事件所属的控件
		self.__methods = WeakList()													# 保存所有事件方法
		self.__shield = False														# 是非屏蔽事件分发

	def __del__( self ) :
		if Debug.output_del_ControlEvent :
			INFO_MSG( "event %s of %s has been delete!" % ( self.__eventName, self.__ownerName ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def isShield( self ) :
		"""
		指出事件是否处于屏蔽状态
		"""
		return self.__shield


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __call__( self, *args ) :
		"""
		触发所有事件
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
		触发一个事件
		"""
		count = method.func_code.co_argcount - 1					# 获取绑定方法的参数数量（不包括 'self' ）
		realCount = len( args )										# 调用时的参数数量（该事件实际应该具备的参数数量）
		if count == realCount :										# 如果方法的参数与实际参数一致
			return method( *args )									# 则直接调用
		elif count == realCount + 1 :								# 如果绑定方法的参数比实际参数多 1
			pyUI = self.__pyWeakUI()								# 则意味着绑定方法要求将事件所属的控件作为第一个参数传递过去
			if pyUI is None :										# 如果事件所属的控件已经不存在
				raise "%s hasbeen disposed!" % self.__ownerName		# 则抛出错误
			return method( pyUI, *args )
		else :
			msg = "the number of arguments are not match!\n"
			msg += "callable object '%s' must contains %d or %d arguments" % ( str( method ), realCount, realCount + 1 )
			raise TypeError( msg )

	# -------------------------------------------------
	def __verify( self, method ) :
		"""
		验证是否是合法的绑定事件方法
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
		获取所有的事件方法
		"""
		return self.__methods.list()

	def getEventName( self ) :
		"""
		获取事件名称
		"""
		return self.__eventName

	def count( self ) :
		"""
		获取事件方法的总数量
		"""
		return len( self.__methods )

	# -------------------------------------------------
	def bind( self, method, add = False ) :
		"""
		绑定一个事件方法
		@type				method : class method
		@param				method : 类的成员方法
		@type				add	   : bool
		@param				add	   : 如果为 True，则可以绑定一个类实例中的多个方法，否则再次绑定的时候，前一次绑定的同一类方法将会被覆盖
		"""
		if not self.__verify( method ) : return				# 验证事件方法释放合法
		cls = getattr( method, "im_class", None )			# 是否是实例方法
		if not add : self.removeClassEvents( cls )			# 如果方法所属实例的类是同一个，则清除原来的方法
		self.__methods.append( method )
		pyUI = self.__pyWeakUI()
		if hasattr( pyUI, 'onEventBinded' ) :				# 有事件绑定时通知所属控件
			pyUI.onEventBinded( self.__eventName, method )

	def unbind( self, method ) :
		"""
		解除绑定一个事件方法
		@type				method : class method
		@param				method : 类的成员方法
		"""
		if method in self.__methods :
			self.__methods.remove( method )
		pyUI = self.__pyWeakUI()
		if hasattr( pyUI, 'onEventUnbinded' ) :				# 有事件取消绑定时通知所属控件
			pyUI.onEventUnbinded( self.__eventName, method )

	# ---------------------------------------
	def removeClassEvents( self, cls ) :
		"""
		清除属于指定某个类成员的所有事件方法
		@type				cls : class
		@param				cls : 类（清除这个类所有实例所有被绑定的方法）
		"""
		for method in self.__methods :
			if not hasattr( method, "im_class" ) :			# 如果不是方法
				continue									# 继续
			if method.im_class is cls :						# 如果方法所属实例的类与指定的类一致
				self.__methods.remove( method )				# 则删除方法

	def clear( self ) :
		"""
		清除所有绑定的事件方法
		"""
		self.__methods.clear()

	# -------------------------------------------------
	def shield( self ) :
		"""
		屏蔽掉事件的触发
		"""
		self.__shield = True

	def unshield( self ) :
		"""
		取消事件触发屏蔽
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
