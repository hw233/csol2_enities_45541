# -*- coding: gb18030 -*-
#
# $Id: Prestige.py,v 1.1 2008-08-30 10:05:25 wangshufeng Exp $

import BigWorld
import csdefine
import csconst
import csstatus

from bwdebug import *

from FactionMgr import factionMgr						# npc��������


class Prestige( dict ):
	"""
	��������Զ������ʹ�������ű�
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		prestigeItems = []
		d = { "items":prestigeItems }
		for prestigeID, value in obj.iteritems():
			prestigeItems.append( { "id": prestigeID, "value": value } )
		return d

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = Prestige()
		for v in dict[ "items" ]:
			obj[ v["id"] ] = v["value"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, Prestige )
		
	def addPrestige( self, factionID, value ):
		"""
		��������
		
		@param factionID : ����factionID
		@type factionID : UINT8
		@param value : ���ӵ�����ֵ
		@type value : INT32
		"""
		if self[ factionID ] >= csconst.PRESTIGE_UPLIMIT and value > 0:	# �����Ѵ����ֵ�������������ˡ�
			return False
		self[ factionID ] += value
		if self[ factionID ] > csconst.PRESTIGE_UPLIMIT:
			self[ factionID ] = csconst.PRESTIGE_UPLIMIT
		if self[ factionID ] < csconst.PRESTIGE_LOWERLIMIT:
			self[ factionID ] = csconst.PRESTIGE_LOWERLIMIT
		return True
		
	def getPrestige( self, factionID ):
		"""
		��ö�ӦfactionID����������
		
		@param factionID : ����factionID
		@type factionID : UINT8
		"""
		return self[ factionID ]
		
	def turnOnPrestige( self, factionID, value ):
		"""
		��������
		
		@param factionID : ����factionID
		@type factionID : UINT8
		@param value : ���ӵ�����ֵ
		@type value : INT32
		"""
		defaultValue = factionMgr.getPrestige( factionID )
		self[ factionID ] = value + defaultValue	# �����Ŀ�����ʽΪ��һ����������ʱ
		
	def initPrestigeDefalut( self ):
		"""
		��ʼ���г�ʼֵ������������ by ����
		"""
		for factionID in factionMgr.factionDict:
			defaultValue = factionMgr.getPrestige( factionID )
			if defaultValue > 0: self[ factionID ] = defaultValue	# ��ʼ������ʱ���������츳������ֱ�ӿ����������츳����
		
		
# �����Զ������͵�ʵ��
instance = Prestige()


#
#$Log: not supported by cvs2svn $
#
