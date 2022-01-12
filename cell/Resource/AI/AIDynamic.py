# -*- coding: gb18030 -*-

# $Id: AIDynamic.py,v 1.1 2008-04-22 04:15:58 kebiao Exp $

import BigWorld
import csstatus
import csdefine
from AIBase import *
from bwdebug import *

class AIDynamic( AIBase ):
	"""
	���ж�̬���ݵ�AI�� ��AI֧����ʱ��¼���ݣ����߸ı�ԭ�л�������
	"""
	def __init__( self ):
		AIBase.__init__( self )
		self._buffer = {}				# ���ڼ�¼��̬���ݵĻ�����
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIBase.init( self, section )

	def setTemp( self, key, val ):
		"""
		�Ը�AI������ʱ������
		@param key: �����ݼ�¼�Ĺؼ���
		@param val: �������ݼ�¼��ֵ ��������Ϊpython���ͣ�  �������κ�ʵ��
		"""
		self._buffer[ key ] = val
		
	def removeTemp( self, key ):
		"""
		�Ը�AIɾ����ʱ������
		@param key: �����ݼ�¼�Ĺؼ���
		"""
		if self._buffer.has_key( key ):
			del self._buffer[ key ]

	def popTemp( self, key, defRetVal ):
		"""
		�Ը�AIɾ����ʱ������
		@param key: �����ݼ�¼�Ĺؼ���
		@param defRetVal: �������û���ҵ����ڵ����� Ĭ�Ϸ���ĳֵ
		"""
		if self._buffer.has_key( key ):
			val = self._buffer[ key ]
			del self._buffer[ key ]
			return val
		return defRetVal
		
	def queryTemp( self, key, defRetVal ):
		"""
		�Ը�AIɾ����ʱ������
		@param key		: �����ݼ�¼�Ĺؼ���
		@param defRetVal: �������û���ҵ����ڵ����� Ĭ�Ϸ���ĳֵ
		"""
		if self._buffer.has_key( key ):
			return self._buffer[ key ]
		return defRetVal
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴AIObjImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�
		
		@return: ����һ��AI���͵��ֵ䡣AI������ϸ���������defs/alias.xml�ļ�
		"""
		return {  "param" : self._buffer }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵ�ai����ϸ�ֵ����ݸ�ʽ�����AIObjImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵ�ai�о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		obj._buffer = data[ "param" ]
		return obj
		
#
# $Log: not supported by cvs2svn $
#