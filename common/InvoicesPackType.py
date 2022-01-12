# -*- coding: gb18030 -*-

"""
This module implements the invoicesPack data type.
@var instance: InvoicesPackType���͵�ʵ������ҪΪ����res\entities\defs\alias.xml��ʵ���Զ����������͡���INVOICEITEMS
@requires: L{InvoiceDataType<InvoiceDataType>}
"""
# $Id: InvoicesPackType.py,v 1.12 2007-05-15 02:54:53 phw Exp $

import Language
import InvoiceDataType
from bwdebug import *

#
#   ��: InvoicesPackType
# ����: Database��Stream��XML Data�ӿ��Լ���װ����ʵ��
#
class InvoicesPackType(dict):
	"""
	ʵ��res\entities\defs\alias.xml�е��Զ�����������INVOICEITEMS
	���а���Database��Stream��XML Data�ӿ��Լ���װ����ʵ��
	
	����������dict�����ֵ���ʽ���Ļ������keyΪЯ��ID��Ψһ�ԣ����ɱ䣻value��InvoiceDataTypeʵ�����á�
	ʹ�÷�ʽ��
		>>> instance = InvoicesPackType()
		>>> instance[toteID] = InvoiceDataType's instance
		
		>>> i = instance[toteID]
		>>> i.xxx( ... )
	"""
	def __init__( self ):
		dict.__init__(self)
		pass

	def __getitem__( self, key ):
		if isinstance(key, int):
			return dict.__getitem__(self, key)
		raise TypeError, "key must int type"

	def __setitem__( self, key, val ):
		if not isinstance(val, InvoiceDataType.InvoiceDataType):
			raise TypeError, "value must 'InvoiceDataType' type"
			return
		if isinstance(key, int):
			# ��һ�������ˣ���Ϊ��Ʒ����û�б���toteID
			#val.setToteId( key )	# ����һ����Ϊ��ȷ��key��InvoiceDataType.toteIdһ��
			dict.__setitem__(self, key, val)
			return
		raise TypeError, "key must \"int\" type"

	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "items":items }
		for k, v in obj.iteritems():
			items.append( { "order" : k, "invoice": v } )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = InvoicesPackType()
		for item in dict["items"]:
			obj[item["order"]] = item["invoice"]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, InvoicesPackType )

### end of class InvoicesPackType() ###

# ����InvoicesPackTypeʵ����res\entities\defs\alias.xml��ʹ��
instance = InvoicesPackType()

#############################
# End of InvoiceDataType.py #
#############################

# $Log: not supported by cvs2svn $
# Revision 1.11  2006/12/21 09:25:31  phw
# ɾ���˼�������Ҫ�ĺ궨��
#
# Revision 1.10  2006/08/09 08:25:26  phw
# ���Զ������͵�ʵ�ַ�ʽ��ΪFIXED_DICT��ʵ�ַ�ʽ
#
# Revision 1.9  2006/03/20 03:18:14  wanhaipeng
# Modify stream for BigWorld 1.7.
#
# Revision 1.8  2006/03/16 07:09:23  wanhaipeng
# Change bind Format.
#
# Revision 1.7  2005/04/29 02:12:57  phw
# �������е���Ʒ�����޸�
#
# Revision 1.6  2005/03/29 09:19:26  phw
# �޸���ע�ͣ�ʹ�����epydoc��Ҫ��
#
# Revision 1.5  2005/03/29 01:35:34  phw
# �޸���ע�ͣ�ʹ�����epydoc��Ҫ��
#
