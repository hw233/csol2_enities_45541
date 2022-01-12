# -*- coding: gb18030 -*-
#
# $Id: TransporterData.py,v 1.1 2007-05-14 00:36:37 panguankong Exp $

"""
��������
"""

import BigWorld
import Language
from bwdebug import *

class TransporterData:
	def __init__( self ):
		"""
		���캯����
		"""
		self.data = {}
		
	def getData( self ):
		"""
		ȡ����������
		"""
		if BigWorld.cellAppData.has_key("Transporters"):
			return BigWorld.cellAppData["Transporters"]
		return None
			
	def __getitem__( self, key ):
		"""
		ȡ��Space���ݲ���
		"""
		objects = getData()
		if objects:
			return objects[key]
		return None

	def register( self, name, sign, pos, direction, spaceName ):
		"""
		ע�ᴫ����
		@param spaceName: ��������
		@type  spaceName: string
		@param name: ����������
		@type  name: string
		@param sign: ������ID
		@type  sign: INT64
		@param pos: �������ش�λ��
		@type  pos: Vector3
		@param pos: �������ش�����
		@type  pos: Vector3
		"""
		objects = {}
		
		door = { "name":name, "pos":pos, "direction":direction }
		
		if BigWorld.cellAppData.has_key("Transporters"):
			objects = BigWorld.cellAppData["Transporters"]
			if objects.has_key( spaceName ):
				objects[spaceName][sign] = door
			else:
				objects[spaceName] = {sign:door}
		else:			
			objects[spaceName] = {sign:door}
		
		BigWorld.cellAppData["Transporters"] = objects


g_transporterData = TransporterData()

def getSpaceData( key ):
	"""
	��ȡ�������ݡ�
		@param key:	������
		@type key:	string
	"""
	return g_transporterData[key]

def register( name, sign, pos, direction, spaceName ):
	"""
	ע�ᴫ����
	@param spaceName: ��������
	@type  spaceName: string
	@param name: ����������
	@type  name: string
	@param sign: ������ID
	@type  sign: INT64
	@param pos: �������ش�λ��
	@type  pos: Vector3
	@param pos: �������ش�����
	@type  pos: Vector3
	"""
	g_transporterData.register( name, sign, pos, direction, spaceName )

def getData():
	"""
	���ش���������	
	"""
	return 	g_transporterData.getData()
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2006/12/21 08:01:06  panguankong
# ���߻�Ҫ���޸��˴��͵�͸������Ϣ
#
# Revision 1.3  2006/12/09 03:18:19  panguankong
# �����Ĺ�ط���
#
# Revision 1.2  2006/11/03 01:22:37  panguankong
# ��ӿռ������
#
# Revision 1.1  2005/12/01 06:38:22  xuning
# ����
#
#
