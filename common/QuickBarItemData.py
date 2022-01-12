# -*- coding: gb18030 -*-
#
# $Id: QuickBarItemData.py,v 1.6 2007-06-14 10:46:50 huangyongwei Exp $

"""
快捷栏项FIXED_DICT
"""

from bwdebug import *
import csdefine

class QuickBarItemData:
	def __init__( self ):
		self.index = 0
		self.qbtype = csdefine.QB_ITEM_NONE
		self.narg1 = 0
		self.sarg2 = ""

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		itemDict = { "index":obj.index, "qbtype":obj.qbtype, "narg1":obj.narg1, "sarg2":obj.sarg2 }
		return itemDict
	
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = QuickBarItemData()
		obj.index = dict["index"]
		obj.qbtype = dict["qbtype"]
		obj.narg1 = dict["narg1"]
		obj.sarg2 = dict["sarg2"]
		return obj

instance = QuickBarItemData()


#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/01/03 08:11:30  phw
# 去掉了注释
#
# Revision 1.4  2006/03/20 03:16:48  wanhaipeng
# Modify stream for BigWorld 1.7.
#
# Revision 1.3  2005/12/23 03:53:31  wanhaipeng
# Add cvslog.
#
#
