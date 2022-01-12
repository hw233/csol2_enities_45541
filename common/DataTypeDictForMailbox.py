# -*- coding: gb18030 -*-
import BigWorld

import cschannel_msgs
import csstatus
from bwdebug import *


class ClassNameMailbox( object ):
	"""
	对战数据基类
	"""
	def __init__( self, className = "", mb = None ):
		object.__init__( self )
		self.className = className
		self.mailbox = mb
	
	def initData( self, dict ):
		self.className = dict[ "className" ]
		self.mailbox = dict[ "mailbox" ]
	
	def getDictFromObj( self, obj ):
		dict = {
			"className" 	: obj.className,
			"mailbox"		: obj.mailbox,
		}
		return dict
	
	def createObjFromDict( self, dict ):
		obj = ClassNameMailbox()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, ClassNameMailbox )

class DataTypeDictForMailbox( object ):
	"""
	战场成员数据管理器
	"""
	def __init__( self ):
		object.__init__( self )
		self.date = {}
	
	def add( self, className, mb ):
		d = ClassNameMailbox( className, mb )
		if self.date.has_key( className ):
			self.date[ className ].append( d )
		else:
			self.date[ className ] = [ d, ]
		
	def get( self, className ):
		if self.date.has_key( className ):
			return self.date[ className ]
		
		return []
	
	def remove( self, className, mb ):
		if self.date.has_key( className ):
			for i, d in enumerate( self.date[ className ] ):
				if d.mailbox.id == mb.id:
					del self.date[ className ][ i ]
					break
		else:
			for dList in self.date.itervalues():
				for i, d in enumerate( dList ):
					if d.mailbox.id == mb.id:
						del dList[ className ][ i ]
						break
	
	def initData( self, dict ):
		for i in dict[ "date" ]:
			self.date[ i.className ] = i

	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "date" ] = obj.date.values()
		return dict
	
	def createObjFromDict( self, dict ):
		obj = DataTypeDictForMailbox()
		obj.initData( dict )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, DataTypeDictForMailbox )

g_classNameMailbox = ClassNameMailbox()
g_dataTypeDictForMailbox = DataTypeDictForMailbox()