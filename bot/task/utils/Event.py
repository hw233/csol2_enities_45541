# -*- coding: gb18030 -*-

from Weaker import WeakList


class Event:

	def __init__( self, name ):
		self._name = name
		self._listeners = WeakList()

	def bind( self, listener ):
		if listener not in self._listeners:
			self._listeners.append(listener)

	def unbind( self, listener ):
		try:
			self._listeners.remove(listener)
		except ValueError, err:
			print "ValueError", err, "invalid listener %s", listener

	def clear( self ):
		self._listeners.clear()

	def listeners( self ):
		return self._listeners.list()

	def listenerAmount( self ):
		return len(self._listeners)

	def trigger( self, *args, **kwargs ):
		for listener in self._listeners:
			listener(*args, **kwargs)

	def name( self ):
		return self._name
