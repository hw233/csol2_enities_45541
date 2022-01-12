# -*- coding: gb18030 -*-

class Event:

	def __init__( self, eventName ):
		self._name = eventName
		self._listeners = []

	def bind( self, listener ):
		"""�󶨼�����"""
		if listener not in self._listeners:
			self._listeners.append( listener )

	def unbind( self, listener ):
		"""��������"""
		if listener in self._listeners:
			self._listeners.remove( listener )

	def trigger( self, *args, **kwagrs ):
		"""�����¼�"""
		for listener in self._listeners:
			listener(*args, **kwagrs)

	def clear( self ):
		"""����¼�"""
		self._listeners = []
