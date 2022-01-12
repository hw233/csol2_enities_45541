# -*- coding: gb18030 -*-

class Event:

	def __init__( self, eventName ):
		self._name = eventName
		self._listeners = []

	def bind( self, listener ):
		"""绑定监听者"""
		if listener not in self._listeners:
			self._listeners.append( listener )

	def unbind( self, listener ):
		"""解绑监听者"""
		if listener in self._listeners:
			self._listeners.remove( listener )

	def trigger( self, *args, **kwagrs ):
		"""触发事件"""
		for listener in self._listeners:
			listener(*args, **kwagrs)

	def clear( self ):
		"""清空事件"""
		self._listeners = []
