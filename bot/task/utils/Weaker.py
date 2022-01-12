# -*- coding: gb18030 -*-
#
# $Id: Weaker.py,v 1.4 2008-06-25 07:11:40 huangyongwei Exp $

"""
This module implements weak reference dates

2008/05/30: writen by huangyongwei
"""

import sys
import weakref
import types
import inspect
import Function
from bwdebug import *

output_del_RefEx		= False						# 是否打印删除 RefEx 信息
output_del_WeakList		= False						# 是否输出删除 WeakList 信息
output_del_WeakSet		= False						# 是否输出删除 WeakSet 信息

# --------------------------------------------------------------------
# metaclass of RefEx
# --------------------------------------------------------------------
class MetaRefEx( type ) :
	def __init__( cls, name, bases, dict ) :
		super( MetaRefEx, cls ).__init__( name, bases, dict )		# 调用基类初始化方法
		cls.__new__ = staticmethod( MetaRefEx.__replace_new )		# 则替换抽象类的实例化方法
		cls.__refObjs = weakref.WeakValueDictionary()				# { ( 引用对象的 ID, 方法名 ) : RefEx 对象 }

	@staticmethod
	def __getMethodKey( method ) :
		if inspect.ismethod( method ) :
			oid = id( method.im_self )
			mname = Function.getMethodName( method )
			return oid, mname
		return id( method )

	def __replace_new( cls, obj, callback = None ) :
		if obj is None or isinstance( obj, RefEx ) :
			return obj
		if not inspect.ismethod( obj ) :							# 如果不是方法
			if not callback :
				return weakref.ref( obj )
			objid = id( obj )
			cbkey = cls.__getMethodKey( callback )
			key = ( objid, cbkey )
			if key in cls.__refObjs :
				return cls.__refObjs[key]
			refObj = object.__new__( cls, obj, callback )			# 新创建一个弱引用对象
			cls.__inst_bind__( refObj, obj, callback )
			cls.__refObjs[key] = refObj
			return refObj
		elif type( obj.im_self ) is types.ClassType :				# 如果是类方法，
			return obj												# 则返回强引用（类常驻内存，不担心泄漏）
		else :
			inst = obj.im_self
			mname = Function.getMethodName( obj )
			objkey = id( inst ), mname
			if callback :											# 如果是实例方法，并且带有回调
				cbkey = cls.__getMethodKey( callback )
				key = ( objkey, cbkey )
			else :
				key = objkey
			refObj = cls.__refObjs.get( key, None )
			if not refObj :
				refObj = object.__new__( cls, obj, callback )		# 新创建一个弱引用对象
				cls.__method_bind__( refObj, inst, mname, callback )
				cls.__refObjs[key] = refObj
			return refObj


class RefEx :
	__metaclass__ = MetaRefEx

	__cg_insts = weakref.WeakValueDictionary()

	def __init__( self, obj, callback = None ) :
		"""
		重新引用另一个对象
		@type				obj		 : instance or None
		@param				obj		 : 对象 或 None，如果是 None，则清空当前的引用
		@type				callback : functor
		@param				callback : 对象删除时的回调，它必须包含一个参数表示被删除的弱引用对象
									   注意：如果传入回调，则回调将会被强引用！
		"""
		self.__cg_insts[id( self )] = self


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __inst_bind__( self, obj, callback = None ) :
		func = Function.Functor( RefEx.__onObjDie, id( self ) )
		self.__refObj = weakref.ref( obj, func )
		self.__callback = callback

	def __method_bind__( self, obj, mname, callback = None ) :
		func = Function.Functor( RefEx.__onObjDie, id( self ) )
		self.__refObj = weakref.ref( obj, func )
		self.__methodName = mname
		self.__callback = callback

	# -------------------------------------------------
	def __repr__( self ) :
		refObj = self()
		if refObj :
			return "instance of RefEx %#0x, ref instance: %s" % ( id( self ), str( refObj ) )
		else :
			return "instance of RefEx %#0x, dead!" % ( id( self ) )

	def __str__( self ) :
		return self.__repr__()

	def __del__( self ) :
		if output_del_RefEx :
			INFO_MSG( "RefEx instance deleted: <%#0X>" % id( self ) )

	def __eq__( self, refEx ) :
		if not isinstance( refEx, RefEx ) : return False
		if self.__refObj != refEx.__refObj : return False
		return getattr( self, "_RefEx__methodName", "" ) == getattr( refEx, "_RefEx__methodName", "" )

	# -------------------------------------------------
	def __call__( self ) :
		"""
		如果引用的对象为可调用对象，则可以直接通过本 RefRex 实例调用
		"""
		refObj = self.__refObj()
		if refObj is None : return None
		if hasattr( self, "_RefEx__methodName" ) :
			return getattr( refObj, self.__methodName )
		return refObj


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __onObjDie( refID, proxy ) :
		self = RefEx.__cg_insts.pop( refID )
		if self.__callback :
			self.__callback( self )
		del self.__callback


# --------------------------------------------------------------------
# implement weak reference object list
# --------------------------------------------------------------------
class WeakList( object ) :
	__shared_dict = { '_WeakList__container' : [] }							# 空链表时的共享属性字典

	__cg_insts = weakref.WeakValueDictionary()

	def __init__( self, objs = None ) :
		"""
		构建一个弱引用链表
		@type				objs	 : WeakList / list
		@param				objs	 : 弱引用链表或链表
		"""
		selfID = id( self )
		self.__cg_insts[selfID] = self

		if objs and len( objs ) :
			self.__peelDict()
			if type( objs ) is WeakList :
				self.__container = objs[:]
			else :
				for e in objs :
					self.__container.append( RefEx( e, self.__cbObjDie ) )
		else :
			self.__shareDict()


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "WeakList" + str( self.list() )

	def __str__( self ) :
		return self.__repr__()

	def __del__( self ) :
		if output_del_WeakList :
			INFO_MSG( "WeakList instance deleted: <%#0X>" % id( self ) )

	# -------------------------------------------------
	def __getitem__( self, index ) :
		return self.__container[index]()

	def __setitem__( self, index, obj ) :
		if index < 0 or index >= len( self.__container ) :
			raise IndexError( "weaklist index out of range!" )
		self.__container[index] = RefEx( obj, self.__cbObjDie )

	def __getslice__( self, x, y ) :
		return self.list()[x : y]

	def __len__( self ) :
		return len( self.__container )

	def __iter__( self ) :
		return self.list().__iter__()

	def __contains__( self, value ) :
		if len( self.__container ) == 0 : return False
		return RefEx( value, self.__cbObjDie ) in self.__container

	# ---------------------------------------
	def __add__( self, wlist ) :
		newList = WeakList()
		if len( wlist.__container ) == 0 and len( self.__container ) == 0 :
			return newList

		newList.__peelDict()
		newList.__container = self.__container[:]
		if type( wlist ) is WeakList :
			newList.__container += wlist.__container
		else :
			for e in wlist :
				newList.__container.append( RefEx( e, newList.__cbObjDie ) )
		return newList

	def __radd__( self, wlist ) :
		newList = WeakList()
		if len( wlist.__container ) == 0 and len( self.__container ) == 0 :
			return newList

		newList.__peelDict()
		if type( wlist ) is WeakList :
			newList.__container = wlist.__container[:]
		else :
			for e in wlist :
				newList.__container.append( RefEx( e, newList.__cbObjDie ) )
		newList.__container += self.__container
		return newList

	def __iadd__( self, wlist ) :
		if len( wlist ) == 0 : return self
		self.__peelDict()
		if type( wlist ) is WeakList :
			self.__container += wlist.__container
		else :
			for e in wlist :
				self.__container.append( RefEx( e, self.__cbObjDie ) )
		return self


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __shareDict( self ) :
		"""
		共享属性字典
		"""
		self.__dict__ = WeakList.__shared_dict

	def __peelDict( self ) :
		"""
		分离属性字典
		"""
		callback = Function.Functor( WeakList.__onObjDie, id( self ) )
		self.__dict__ = {
			'_WeakList__container' : [],
			'_WeakList__cbObjDie' : callback }

	# -------------------------------------------------
	@staticmethod
	def __onObjDie( oid, proxy ) :
		"""
		当一个对象销毁时被调用
		"""
		self = WeakList.__cg_insts[oid]
		pid = id( proxy )
		count = len( self.__container )
		for i in xrange( count - 1, -1, -1 ) :
			refObj = self.__container[i]
			if id( refObj ) == pid :
				self.__container.remove( refObj )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def list( self ) :
		"""
		返回链表中的强引用对象
		@rtype				: list
		@param				: instance of list
		"""
		return [refObj() for refObj in self.__container]

	def count( self ) :
		"""
		返回链表元素数量
		@rtype				: int
		@return				: 链表元素个数
		"""
		return len( self.__container )

	# -------------------------------------------------
	def append( self, obj ) :
		"""
		添加一个对象到弱引用链表
		@type			obj : Instance
		@param			obj : 实例
		"""
		if obj is None :
			raise TypeError( "WeakList's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		self.__container.append( RefEx( obj, self.__cbObjDie ) )

	def appends( self, objs ) :
		"""
		最佳一组对象到弱引用列表
		@type			objs : Instance
		@param			objs : 实例列表
		"""
		if None in objs :
			raise TypeError( "WeakList's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		for obj in objs :
			self.__container.append( RefEx( obj, self.__cbObjDie ) )

	def insert( self, index, obj ) :
		"""
		插入一个对象
		@type			index : int
		@param			index : 要插入的索引
		@type			obj	  : Instance
		@param			obj	  : 对象
		"""
		if obj is None :
			raise TypeError( "WeakList's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		self.__container.insert( index, RefEx( obj, self.__cbObjDie ) )

	def inserts( self, index, objs ) :
		"""
		插入一组对象
		@type			index : int
		@param			index : 要插入的索引
		@type			objs  : list
		@param			objs  : 要插入的一组对象
		"""
		if None in objs :
			raise TypeError( "WeakList's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		for idx in xrange( len( objs ) - 1, -1, -1 ) :
			self.__container.insert( index, RefEx( objs[idx], self.__cbObjDie ) )

	def remove( self, obj ) :
		"""
		删除一个对象
		@type			obj : Instance
		@param			obj : 要删除的对象
		"""
		refObj = RefEx( obj, self.__cbObjDie )
		if refObj in self.__container :
			self.__container.remove( refObj )
			if len( self.__container ) == 0 :
				self.__shareDict()

	def pop( self, back = True ) :
		"""
		弹出一个元素
		@type				back : int
		@param				back : 是否是弹出后面的
		@rtype					 : Instance
		@return					 : 链表中最后或最前面的一个元素
		"""
		elem = None
		if back :
			elem = self.__container.pop()()
		else :
			elem = self.__container.pop( 0 )()
		if len( self.__container ) == 0 :
			self.__shareDict()
		return elem

	def clear( self ) :
		"""
		清空弱引用链表
		"""
		self.__shareDict()


# --------------------------------------------------------------------
# implement weak reference object set
# --------------------------------------------------------------------
class WeakSet( object ) :
	__shared_dict = { '_WeakSet__container' : set() }							# 空链表时的共享属性字典

	__cg_insts = weakref.WeakValueDictionary()

	def __init__( self, objs = None ) :
		"""
		构建一个弱引用链表
		@type				objs	 : WeakSet / list
		@param				objs	 : 弱引用链表或链表
		"""
		selfID = id( self )
		self.__cg_insts[selfID] = self

		if objs and len( objs ) :
			self.__peelDict()
			if type( objs ) is WeakSet :
				self.__container.update( objs )
			else :
				for e in objs :
					self.__container.add( RefEx( e, self.__cbObjDie ) )
		else :
			self.__shareDict()


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "WeakSet" + str( self.set() )

	def __str__( self ) :
		return self.__repr__()

	def __del__( self ) :
		if output_del_WeakSet :
			INFO_MSG( "WeakSet instance deleted: <%#0X>" % id( self ) )

	# -------------------------------------------------
	def __len__( self ) :
		return len( self.__container )

	def __iter__( self ) :
		return self.set().__iter__()

	def __contains__( self, value ) :
		if len( self.__container ) == 0 : return False
		return RefEx( value, self.__cbObjDie ) in self.__container


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __shareDict( self ) :
		"""
		共享属性字典
		"""
		self.__dict__ = WeakSet.__shared_dict

	def __peelDict( self ) :
		"""
		分离属性字典
		"""
		callback = Function.Functor( WeakSet.__onObjDie, id( self ) )
		self.__dict__ = {
			'_WeakSet__container' : set(),
			'_WeakSet__cbObjDie' : callback }

	# -------------------------------------------------
	@staticmethod
	def __onObjDie( oid, proxy ) :
		"""
		当一个对象销毁时被调用
		"""
		self = WeakSet.__cg_insts[oid]
		self.__container.remove( proxy )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def set( self ) :
		"""
		返回链表中的强引用对象
		@rtype				: list
		@param				: instance of list
		"""
		return [refObj() for refObj in self.__container]

	def count( self ) :
		"""
		返回链表元素数量
		@rtype				: int
		@return				: 链表元素个数
		"""
		return len( self.__container )

	# -------------------------------------------------
	def add( self, obj ) :
		"""
		添加一个对象到弱引用链表
		@type			obj : Instance
		@param			obj : 实例
		"""
		if obj is None :
			raise TypeError( "WeakSet's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		self.__container.add( RefEx( obj, self.__cbObjDie ) )

	def adds( self, objs ) :
		"""
		最佳一组对象到弱引用列表
		@type			objs : Instance
		@param			objs : 实例列表
		"""
		if None in objs :
			raise TypeError( "WeakSet's element must't be None." )
		if len( self.__container ) == 0 :
			self.__peelDict()
		for obj in objs :
			self.__container.add( RefEx( obj, self.__cbObjDie ) )

	def update( self, objs ) :
		"""
		更新集合
		"""
		self.adds( objs )

	def remove( self, obj ) :
		"""
		删除一个对象
		@type			obj : Instance
		@param			obj : 要删除的对象
		"""
		refObj = RefEx( obj, self.__cbObjDie )
		if refObj in self.__container :
			self.__container.remove( refObj )
			if len( self.__container ) == 0 :
				self.__shareDict()

	def clear( self ) :
		"""
		清空弱引用链表
		"""
		self.__shareDict()

