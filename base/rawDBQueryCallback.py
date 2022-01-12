# -*- coding: gb18030 -*-

# $Id: rawDBQueryCallback.py,v 1.1 2006-04-19 10:48:24 phw Exp $

"""
�ֶ���ѯ���ݿ��׼�ص�
"""
import struct
from bwdebug import *

def rawDBQueryCallback( result ):
	"""
	��ȡ������Ϣ�ص�
	
	@param result: see also "Execute Commands on SQL Database" from server_scripting_guide.pdf
	@type  result: string
	@return: list of list as [ [ field1, field2, ... ], ... ]�����ص����ַ����б����Ľ��������"select"��ѯ���
	"""
	if not isinstance( result, str):
		DEBUG_MSG( "No output from database", ["(failed)","(succeeded)"][result] )
		return []
	# print repr(result)
	#DEBUG_MSG( repr(result) )
	(rows, cols) = struct.unpack( "<ii", result[:8] )
	result = result[8:]
	msgList = []
	for row in xrange( rows ):
		colslist = []
		for col in xrange( cols ):
			# cols format like as: field1, field2, ...
			dataPtr = 1;
			(size,) = struct.unpack( "B", result[0] )
			if (size == 0xFF):
				# i.e. biglength use next three bytes as
				# the proper data length
				dataPtr = 4
				(size,) = struct.unpack( "<i", result[0:dataPtr] )
				size >>= 8
			
			SQLData = result[dataPtr:size+dataPtr]
			result = result[size+dataPtr:]
			colslist.append( SQLData )	# appen each col data to list
		msgList.append( colslist )		# append each row to list
	return msgList	# the end
