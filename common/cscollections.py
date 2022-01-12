# -*- coding: gb18030 -*-
#
# $Id: cscollections.py,v 1.25 2008-07-12 06:53:09 huangyongwei Exp $

"""
data constructors��
-- 2006/10/14 : by huangyw
"""


# --------------------------------------------------------------------
# class of stack
# --------------------------------------------------------------------
class Stack :
	def __init__( self ) :
		self.__container = []

	# ----------------------------------------------------------------
	# inner
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Stack(%s)" % str( self.__container )

	def __str__( self ) :
		return self.__repr__()

	def __iter__( self ) :
		return self.__container.__iter__()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def push( self, data ) :
		"""
		push data object
		"""
		self.__container.append( data )

	def pop( self ) :
		"""
		pop data object
		"""
		top = self.top()
		if top is not None :
			self.__container.remove( top )
		return top

	def pushs( self, datas ) :
		"""
		push a list of datas
		"""
		self.__container += datas

	# -------------------------------------------------
	def top( self ) :
		"""
		get the top element
		"""
		if len( self.__container ) > 0 :
			return self.__container[-1]
		return None

	def bottom( self ) :
		"""
		get the bottom element
		"""
		if len( self.__container ) > 0 :
			return self.__container[0]
		return None

	def size( self ) :
		"""
		get the number of elements
		"""
		return len( self.__container )

	def isIn( self, data ) :
		"""
		indicate whether the data is in stack
		"""
		return data in self.__container

	def empty( self ) :
		"""
		empty the stack
		"""
		self.__container = []


# --------------------------------------------------------------------
# class of queue
# --------------------------------------------------------------------
class Queue :
	def __init__( self ) :
		self.__container = []

	# ----------------------------------------------------------------
	# inner
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Queue(%s)" % str( self.__container )

	def __str__( self ) :
		return self.__repr__()

	def __iter__( self ) :
		return self.__container.__iter__()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enter( self, data ) :
		"""
		data object enter queue
		"""
		self.__container.append( data )

	def leave( self ) :
		"""
		data object leave queue
		"""
		if len( self.__container ) > 0 :
			data = self.__container[0]
			del self.__container[0]
			return data
		return None

	def enters( self, datas ) :
		"""
		enter a list of datas
		"""
		self.__container += datas

	# -------------------------------------------------
	def head( self ) :
		"""
		get the head element
		"""
		if len( self.__container ) > 0 :
			return self.__container[0]
		return None

	def tail( self ) :
		"""
		get the tail element
		"""
		if len( self.__container ) > 0 :
			return self.__container[-1]
		return None

	def length( self ) :
		"""
		get the number of queue
		"""
		return len( self.__container )

	def isIn( self, data ) :
		"""
		indicate whether the data is in queue
		"""
		return data in self.__container

	def clear( self ) :
		"""
		clear the queue
		"""
		self.__container = []


# --------------------------------------------------------------------
# class of order cycle list
# --------------------------------------------------------------------
class CycleList :
	def __init__( self, eles = None ) :
		if eles is None :
			self.__container = []
		elif type( eles ) is list :
			self.__container = eles[:]
		if len( self.__container ) > 0 :
			self.__current = 0
		else :
			self.__current = -1


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		s = "CycleList"
		s += str( self.__container )
		return s

	def __str__( self ) :
		return self.__repr__()

	# ---------------------------------------
	def __len__( self ) :
		return len( self.__container )

	def __contains__( self, value ) :
		return value in self.__container

	def __iter__( self ) :
		return self.__container.__iter__()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def count( self ) :
		"""
		return the number of elements
		"""
		return len( self.__container )

	def list( self ) :
		"""
		list all origent element
		"""
		return self.__container[:]

	def elements( self ) :
		"""
		get all values
		"""
		if self.count() == 0 : return []
		return self.__container[self.__current:] + self.__container[:self.__current]

	# -------------------------------------------------
	def append( self, value, pointNew = False ) :
		"""
		append an enlement behind current element
		"""
		if self.__current < 0 :
			self.__container.append( value )
			self.__current = 0
		elif self.__current == self.count() - 1 :
			self.__container.append( value )
		else :
			self.__container.insert( self.__current + 1, value )
		if pointNew :
			self.next()

	def insert( self, value, pointNew = False ) :
		"""
		insert an element before current element
		"""
		if self.__current < 1 :
			self.__container.append( value )
			self.__current = 0
		else :
			self.__container.insert( self.__current, value )
		if pointNew :
			self.fore()

	def remove( self, value ) :
		"""
		remove elements which value is the given argument
		"""
		while value in self.__container :
			self.__container.remove( value )
		if self.__current >= self.count() :
			self.__current = self.count() - 1

	def clear( self ) :
		"""
		clear all elements
		"""
		self.__container = []
		self.__current = -1

	# -------------------------------------------------
	def origin( self ) :
		"""
		get the first push element
		"""
		assert self.count() > 0, "empty cycle list"
		return self.__container[0]

	def current( self ) :
		"""
		get current element
		"""
		assert self.count() > 0, "empty cycle list"
		return self.__container[self.__current]

	def fore( self ) :
		"""
		get fore element relative to the current element and move current pointer to it
		"""
		self.__current = ( self.__current - 1 ) % self.count()
		return self.current()

	def next( self ) :
		"""
		get next element relative to current element and move current pointer to it
		"""
		self.__current = ( self.__current + 1 ) % self.count()
		return self.current()

	def pry( self, count ) :
		"""
		pry element relative to current element
		"""
		assert self.__current >= 0, "empty cycle list!"
		index = ( self.__current + count ) % self.count()
		return self.__container[index]

	# ---------------------------------------
	def seek( self, count ) :
		"""
		seek pointer to anther seat relative to current element
		"""
		self.__current = ( self.__current + count ) % self.count()

	def goto( self, value ) :
		"""
		set current pointer point at an element which it's value is the given argument
		"""
		assert value in self.__container, "value is not in cycle list!"
		self.__current = self.__container.index( value )

	def resume( self ) :
		"""
		set current pointer point to the origin element
		"""
		if self.count() > 0 :
			self.__current = 0


# --------------------------------------------------------------------
# class of order maplist
# --------------------------------------------------------------------
class MapList :
	class __defValue : pass

	def __init__( self ) :
		self.__container = []

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "MapList" + str( self.__container )

	def __str__( self ) :
		return self.__repr__()

	def __getitem__( self, key ) :
		index = self.__getIndex( key )
		if index == -1 :
			raise Exception( "key %s is not exist!" % key )
		return self.__container[index][1]

	def __setitem__( self, key, value ) :
		index = self.__getIndex( key )
		if index == -1 :
			self.__container.append( ( key, value ) )
		else :
			self.__container[index] = ( key, value )

	def __delitem__( self, key ) :
		index = self.__getIndex( key )
		if index == -1 : return
		self.__container.pop( index )

	def __len__( self ) :
		return len( self.__container )

	def __eq__( self, ml ) :
		if ml.count != self.count : return False
		for index in self.count :
			if ml[index] != self.__container[index] :
				return False
		return True

	def __iter__( self ) :
		return self.keys().__iter__()

	def __contains__( self, key ) :
		for k, v in self.__container :
			if k == key : return True
		return False

	def __copy__( self ) :
		m = MapList()
		m.__container = self.__container[:]
		return m


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getIndex( self, key ) :
		"""
		get index via key
		"""
		index = -1
		for i, ( k, value ) in enumerate( self.__container ) :
			if k != key : continue
			index = i
			break
		return index


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def append( self, ( key, value ) ) :
		"""
		append an item which contain key and value
		"""
		self.__container.append( ( key, value ) )

	def insert( self, index, ( key, value ) ) :
		"""
		insert an item
		"""
		self.__container.insert( index, ( key, value )  )

	def has_key( self, key ) :
		"""
		indidate whether the maplist contain an item which it's key is argument key
		"""
		index = self.__getIndex( key )
		return index != -1

	def has_value( self, value ) :
		"""
		indicate whether the value is in me
		"""
		for key, v in self.__container :
			if v == value :
				return True
		return False

	def index( self, key ) :
		"""
		get index of the item which it's key is argument key
		"""
		return self.__getIndex( key )

	def count( self ) :
		"""
		get the number of items
		"""
		return len( self.__container )

	# -------------------------------------------------
	def items( self ) :
		"""
		return all items map to list
		"""
		return self.__container[:]

	def keys( self ) :
		"""
		get a list of keys
		"""
		return [key for ( key, value ) in self.__container]

	def values( self ) :
		"""
		get a list of values
		"""
		return [value for ( key, value ) in self.__container]

	# ---------------------------------------
	def iteritems( self ) :
		"""
		return all items map to list
		"""
		return iter( self.__container )

	def iterkeys( self ) :
		"""
		get a list of keys
		"""
		return iter( key for ( key, value ) in self.__container )

	def itervalues( self ) :
		"""
		get a list of values
		"""
		return iter( value for ( key, value ) in self.__container )

	# -------------------------------------------------
	def get( self, key, defValue = None ) :
		if self.has_key( key ) :
			return self[key]
		return defValue

	def getByIndex( self, index ) :
		return self.__container[index]

	def pop( self, key, defValue = __defValue ) :
		"""
		pop up an item
		"""
		index = self.__getIndex( key )
		if index == -1 :
			if defValue == MapList.__defValue :
				raise KeyError( "key %s is not exist!" % key )
			else :
				return defValue
		return self.__container.pop( index )[1]

	def clear( self ) :
		"""
		clear all items
		"""
		self.__container = []

	# ---------------------------------------
	def sort( self, cmp = None, key = None, reverse = False ) :
		self.__container.sort( cmp, key, reverse )

	def sortByKey( self, revs = False ) :
		self.__container.sort( key = lambda item : item[0], reverse = revs )

	def reverse( self ) :
		self.__container.reverse()


# --------------------------------------------------------------------
# class of free dictionary
# --------------------------------------------------------------------
class FreeDict( dict ) :
	def __init__( self, dic = None ) :
		if dic is not None :
			self.clear()
			self.update( dic )

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		s = "{%s}" % ( len( self ) * '%s, ' )
		s = s.replace( ", }", "}" )
		eles = []
		for key, value in self.iteritems() :
			if type( key ) is str or type( key ) is unicode :
				key = "'%s'" % key
			if type( value ) is str or type( value ) is unicode :
				value = "'%s'" % value
			ele = "[%s]: (%s)" % ( key, value )
			eles.append( ele )
		s = s % tuple( eles )
		return s

	def __str__( self ) :
		return self.__repr__()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __call__( self, value ) :
		for key, v in self.iteritems() :
			if v is value :
				return key
		raise "value is not exist!"


class DifferMap :
	"""
	��¼ֵ�Ƿ����ı������
	"""
	def __init__( self ) :
		self.__container = {}								# �������ֵ���ֵ�{ key:Pair( originValue, currentValue )}
		self.__alteredKeys = set()							# ������иı��˵�ֵ( �ɼӿ�ı�ֵ�������ٶ� )

	def __getitem__( self, key ) :
		"""
		����˷������ͨ��instance[ key ]�ķ�ʽ��ȡֵ
		"""
		return self.__container[ key ].second

	def __setitem__( self, key, value ) :
		"""
		����˷������ͨ��instance[ key ] = value �ķ�ʽ����ֵ
		"""
		if self.has_key( key ) :
			self.__setNewValue( key, value )
		else :
			self.__container[ key ] = Pair( value, value )

	def __delitem__( self, key ) :
		"""
		����˷������ͨ��del instance[ key ] �ķ�ʽɾ��ֵ
		"""
		del self.__container[ key ]
		if key in self.__alteredKeys :
			self.__alteredKeys.remove( key )

	def __contains__( self, key ) :
		"""
		����Ƿ����ĳ���ؼ���
		"""
		return key in self.__container

	def __iter__( self ) :
		"""
		����˷������ͨ��iter( instance ) �ķ�ʽ�õ�������
		"""
		return self.__container.iterkeys()

	def __len__( self ) :
		"""
		����˷������ͨ��len( instance ) �ķ�ʽ��ȡֵ������
		"""
		return len( self.__container )

	def __setNewValue( self, key, value ) :
		"""
		��������ֵ
		"""
		originAltered = self.isValueAltered( key )
		self.__container[ key ].second = value
		currentAltered = self.__checkValueAltered( key )
		if currentAltered and not originAltered :			# ���ֵ�Ƿ����ı�
			self.__alteredKeys.add( key )
		elif originAltered and not currentAltered :
			self.__alteredKeys.remove( key )

	def __checkValueAltered( self, key ) :
		"""
		���ؼ��ֶ�Ӧ��ֵ�Ƿ����ı�
		"""
		return self[key] != self.origin( key )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def items( self ) :
		"""
		��ȡ��ǰֵ�ֵ�
		"""
		return dict( (k, v.second) for k, v in self.__container.iteritems() )

	def origin( self, key ) :
		"""
		��ȡ��ʼֵ
		"""
		return self.__container[key].first

	def has_key( self, key ) :
		"""
		�Ƿ���ڹؼ���
		"""
		return self.__container.has_key( key )

	def get( self, key, default = None ) :
		"""
		��ȡ�ؼ��ֶ�Ӧ��ֵ
		"""
		if key in self.__container :
			return self[ key ]
		return default

	def addNew( self, key, value ) :
		"""
		��Ϊһ��������ӵ������У�����Ѵ��ڣ����ȰѾɵ�ɾ����
		"""
		if self.has_key( key ) :
			self.remove( key )
		self[ key ] = value

	def remove( self, key ) :
		"""
		�Ƴ��ؼ��ּ���Ӧ��ֵ
		"""
		self.__delitem__( key )

	def isAltered( self ) :
		"""
		�Ƿ���ֵ�����˸ı�
		"""
		return len( self.__alteredKeys ) != 0

	def isValueAltered( self, key ) :
		"""
		�Ƿ�ؼ��ֶ�Ӧ��ֵ�����˸ı�
		"""
		return key in self.__alteredKeys

	def getAlteredItems( self ) :
		"""
		��ȡ���иı���
		"""
		result = {}
		for key in self.__alteredKeys :
			result[ key ] = self[ key ]
		return result

	def getUnalteredItems( self ) :
		"""
		��ȡ����δ�ı����
		"""
		unalteredKeys = set( self.__container.iterkeys() ) - self.__alteredKeys
		result = {}
		for key in unalteredKeys :
			result[ key ] = self[ key ]
		return result

	def clear( self ) :
		"""
		"""
		self.__container.clear()
		self.__alteredKeys.clear()


class Pair( object ) :
	"""
	��Ԫ�����
	"""
	__slots__ = ( "first", "second" )

	def __init__( self, first, second ) :
		object.__init__( self )
		self.first = first
		self.second = second

	def __repr__( self ) :
		return "Pair(%s,%s)" % ( str(self.first), str(self.second) )

	def __str__( self ) :
		return self.__repr__()

	def __eq__( self, pairObj ) :
		return pairObj.first == self.first and pairObj.second == self.second
