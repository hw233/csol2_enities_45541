# -*- coding: gb18030 -*-

from CrondScheme import Scheme
import time

class TimeScales:
	"""
	ά�����ʱ��Ρ�
	��Ҫ�������ж�һ��ʱ����Ƿ�����Щʱ����е�����һ��ʱ�����
	"""
	def __init__( self ):
		"""
		"""
		self._schemes = []
		self._persistSecond = 0					#����ʱ�䣨��λ���룩
	
	
	def init( self, schemesString, persistSecond ):
		"""
		"""
		for s in schemesString.split( "|" ):
			self._schemes.append( Scheme( s ) )
		
		self._persistSecond = persistSecond
		
	def isInScale( self, year, month, day, hour, minute ):
		"""
		�Ƿ�����Щʱ�����
		"""
		testTime = time.mktime( (year, month, day, hour, minute, 0, 0, 0, 0 ) )
		
		beginTime = time.mktime( time.localtime( testTime - self._persistSecond ) )
		
		beginTimeTuple = time.localtime( beginTime )
		
		for scheme in self._schemes:
			if scheme.calculateNext( beginTimeTuple[0], beginTimeTuple[1], beginTimeTuple[2], beginTimeTuple[3], beginTimeTuple[4] ) < testTime:
				return True
		return False