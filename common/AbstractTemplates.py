# -*- coding: gb18030 -*-
#
# $Id: InputBase.py,v 1.19 2008-06-21 01:48:39 huangyongwei Exp $

"""
该模块主要放置一些设计模式相关的模式基类或模式向导

2009.01.20 : writen by huangyongwei
2010.05.10 : add 'MultiLngFuncDecorator' class
"""

import re
from bwdebug import *
from Weaker import WeakList

# --------------------------------------------------------------------
# 单例类型类
# 该程序实现了单例类的类，在类的类中控制类对象的生成方式，
# 从而将设计模式中的单件实现，由过去的约定方式修改为技术上的支持。
# --------------------------------------------------------------------
class MetaSingletonClass( type ) :
	def __init__( cls, name, bases, dict ) :
		super( MetaSingletonClass, cls ).__init__( name, bases, dict )	# 调用基类初始化函数
		cls.__inst = None
		cls.__initer = cls.__init__
		cls.__new__ = staticmethod( MetaSingletonClass.__replace_new )	# 重新定位单件类的实例化方法

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def insted( cls ) :
		"""
		是否已经初始化了单件实例
		"""
		return cls.__inst is not None

	@property
	def inst( cls ) :
		"""
		获取单件实例
		"""
		return cls()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __replace_init( inst, *args, **kwds ) :
		"""
		替换构造 init
		"""
		pass

	@staticmethod
	def __replace_new( cls, *args, **kwds ) :
		"""
		新的替换 new
		"""
		if cls.__inst is None :
			cls.__inst = object.__new__( cls, *args, **kwds )
			cls.__init__( cls.__inst, *args, **kwds )
			cls.__init__ = MetaSingletonClass.__replace_init
		return cls.__inst

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def releaseInst( cls ) :
		"""
		释放掉当前实例
		"""
		cls.__inst = None
		cls.__init__ = cls.__initer


# -----------------------------------------------------
# 单例基类，如果某个类继承于 Singleton，则该类将会自动成为单例类
# -----------------------------------------------------
class Singleton( object ) :
	__metaclass__ = MetaSingletonClass										# 强制单例类的类为 MetaSingletonClass


# --------------------------------------------------------------------
# 抽象类类型
# 该程序实现了抽象类的类，在类的类中控制类对象的生成方式，从而控制类的抽象化
# --------------------------------------------------------------------
class MetaAbstractClass( type ) :
	def __init__( cls, name, bases, dict ) :
		super( MetaAbstractClass, cls ).__init__( name, bases, dict )		# 调用基类初始化方法
		if cls.isAbstract() :												# 如果是抽象类
			cls.__new__ = staticmethod( MetaAbstractClass.__replace_new )	# 则替换抽象类的实例化方法
		else :
			for method in cls.__getImplementedMethods() :
				mname = method.func_name
				myfunc = getattr( cls, mname ).im_func
				assert myfunc != method, "class %s must implement method %s" % ( cls.__name__, mname )
			cls.__new__ = object.__new__

	def __getAbstractMethods( cls ) :
		"""
		获取当前要实现的类的抽象方法，如果该类不是抽象类，则返回 None
		"""
		methodName = "_%s__abstract_methods" % cls.__name__
		methodName = re.sub( "^_*", "_", methodName )
		return getattr( cls, methodName, None )

	def __getImplementedMethods( cls ) :
		"""
		获取当前类需要实现的抽象方法
		"""
		methods = set()
		for base in cls.__bases__ :
			if hasattr( base, "_MetaAbstractClass__getAbstractMethods" ) :
				abstractMethods = base.__getAbstractMethods()
				if abstractMethods is None : continue
				methods.update( abstractMethods )
		return methods

	def __replace_new( cls, *args, **kwds ) :
		"""
		替换抽象类的实例化方法
		"""
		raise TypeError( "abstract class '%s' is not allow to be instanced!" % cls.__name__ )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isAbstract( cls ) :
		"""
		是否是抽象类
		"""
		return cls.__getAbstractMethods() is not None


# -----------------------------------------------------
# 抽象类基类，继承于该类的类，则为抽象类
# 如果继承于该类的类，带有 __abstract_methods 类成员，
#	则继承的新类，仍然是一个抽象类（不能实例化）
# 如果调用 __abstract_methods.add() 把一个成员方法添加到 __abstract_methods 中，
# 	则添加到 __abstract_methods 中的方法都为抽象方法，需要在子类中实现它们
# -----------------------------------------------------
class AbstractClass( object ) :
	__metaclass__ = MetaAbstractClass										# 强制类的超类为 MetaSingletonClass
	__abstract_methods = set()



# --------------------------------------------------------------------
# 事件代理基类
# 该类实现了一个事件代理，通过该代理，可以绑定多个 callback，从而实现
#	  事件触发代理后，可以触发多个 callback
# --------------------------------------------------------------------
class EventDelegate( object ) :
	"""
	事件类( 注意：绑定的方法一定是实例方法 )
	"""
	def __init__( self ) :
		self.__handlers = WeakList()		# 保存所有事件收听者函数
		self.__shield = False				# 是否屏蔽事件代理（屏蔽后，接收者将收不到事件触发）


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def isShield( self ) :
		"""
		是否屏蔽事件代理（屏蔽后，接收者将收不到事件触发）
		"""
		return self.__shield

	@property
	def handlerCount( self ) :
		"""
		获取事件方法的总数量
		"""
		return len( self.__handlers )


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __call__( self, *args ) :
		"""
		触发代理
		"""
		if self.__shield : return False
		res = False
		for handler in self.__handlers :
			try :
				res = handler( *args ) or res
			except :
				EXCEHOOK_MSG( str( method ) )
		return res


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def bind( self, handler ) :
		"""
		绑定一个收听者函数
		@type				handler : callable object
		@param				handler : 事件接收者的可调用对象
		"""
		if handler in self.__handlers :
			ERROR_MSG( "%s has been in delegate list!" % str( handler ) )
		else :
			self.__handlers.append( handler )

	def unbind( self, handler ) :
		"""
		解除绑定一个代理绑定
		@type				handler : callable object
		@param				handler : 事件接收者的可调用对象
		"""
		if handler in self.__handlers :
			self.__handlers.remove( handler )

	# -------------------------------------------------
	def getHandlers( self ) :
		"""
		获取所有的事件方法
		"""
		return self.__handlers.list()

	def hasHandler( self, handler ) :
		"""
		指出代理中是否有指定事件接收对象
		"""
		return handler in self.__handlers

	def clearHandlers( self ) :
		"""
		清除所有绑定的事件方法
		"""
		self.__handlers.clear()

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
# 多语言版本的函数装饰器
# 该类实现了一个函数或方法的装饰器，使得编译期（严格来说是 import 期）
#	  就能根据不同语言版本，使用不同的函数或方法实现不同的功能
#
# 使用方法：
#	  使自定义的函数装饰器继承于 MultiLngFuncDecorator，然后在自定义的装饰器中
#	  实现不同语言版本的实现方法。
# --------------------------------------------------------------------
from Language import LANG_CONFIG_STRING as METHOD_NAME

class MetaMultiLngFuncDecorator( type ) :
	# ---------------------------------------
	# 函数封装器
	# ---------------------------------------
	class FWarp( object ) :
		__slots__ = ( "__func" )
		def __init__( self, f ) :
			self.__func = f
		def __call__( self, *args, **darg ) :
			return self.__func( *args, **darg )

	# ---------------------------------------
	# 函数实现前的装饰
	# ---------------------------------------
	def __init__( cls, name, bases, dict ) :
		super( MetaMultiLngFuncDecorator, cls ).__init__( name, bases, dict )
		cls.originalFunc = None

	def __call__( cls, func ) :
		assert cls.originalFunc is None, "muti-language function '%r' decorator has decorated!" % cls
		cls.originalFunc = MetaMultiLngFuncDecorator.FWarp( func )
		baseFunc = getattr( MultiLngFuncDecorator, METHOD_NAME, func )
		subFunc = getattr( cls, METHOD_NAME, func )
		if baseFunc is subFunc :
			return func
		return subFunc

# -----------------------------------------------------
# 注意：
#	  ① 这些实现方法必需是静态的
#	  ② 这些实现方法名称必需是 Language::LANG_STRING_MARKS 对应的名称
#	  ③ 如果没有编写某种语言版本的实现方法，则默认使用原始函数的实现
#	  ④ 通过 deco.originalFunc() 可以获得原始函数
#	  ⑤ 如果同时有其他装饰器：@staticmethod、@classmethod，则这些装饰器
#		 必需置于本装饰器的前面。
# -----------------------------------------------------
class MultiLngFuncDecorator( object ) :
	__metaclass__ = MetaMultiLngFuncDecorator

	# ----------------------------------------------------------------
	@staticmethod
	def locale_default( *args, **darg ) :
		"""
		LANG_GBK 的实现方案，如果不编写该函数，则在 LANG_GBK 版本下，默认使用原始版本
		"""
		return MultiLngFuncDecorator.originalFunc( *args, **darg )			# 原始函数

	@staticmethod
	def locale_big5( *args, **darg ) :
		"""
		LANG_BIG5 的实现方案，如果不编写该函数，则在 LANG_BIG5 版本下，默认使用原始版本
		"""
		return MultiLngFuncDecorator.originalFunc( *args, **darg )			# 原始函数
