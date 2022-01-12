# -*- coding: gb18030 -*-

from CrondScheme import Scheme
import time

class TimeScales:
	"""
	维护多个时间段。
	主要作用是判定一个时间点是否在这些时间段中的任意一个时间段内
	"""
	def __init__( self ):
		"""
		"""
		self._schemes = []
		self._persistSecond = 0					#持续时间（单位：秒）
	
	
	def init( self, schemesString, persistSecond ):
		"""
		"""
		for s in schemesString.split( "|" ):
			self._schemes.append( Scheme( s ) )
		
		self._persistSecond = persistSecond
		
	def isInScale( self, year, month, day, hour, minute ):
		"""
		是否在这些时间段内
		"""
		testTime = time.mktime( (year, month, day, hour, minute, 0, 0, 0, 0 ) )
		
		beginTime = time.mktime( time.localtime( testTime - self._persistSecond ) )
		
		beginTimeTuple = time.localtime( beginTime )
		
		for scheme in self._schemes:
			if scheme.calculateNext( beginTimeTuple[0], beginTimeTuple[1], beginTimeTuple[2], beginTimeTuple[3], beginTimeTuple[4] ) < testTime:
				return True
		return False