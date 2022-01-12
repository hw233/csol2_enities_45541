# -*- coding: gb18030 -*-

# $Id: CKaStone.py,v 1.3 2008-05-17 11:42:42 huangyongwei Exp $

"""
魂魄石基础类
"""
from CEquip import *
from bwdebug import *
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

class CKaStone( CEquip ):
	"""
	魂魄石基础类
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取装备专有描述信息
		"""
		CEquip.getProDescription( self, reference )
		attrMap = ItemAttrClass.m_itemAttrMap
		ka_count = attrMap["ka_count"].description( self, reference )
		self.desFrame.SetDescription( "eq_hardiness" , ka_count )

	def set( self, attrName, value, owner = None ):
		"""
		设置动态数据

		@param owner: 如果值为None，则只设置数量；如果值(只能)为Role实例，则调用entity.client.onItemAttrUpdated()方法
		@return: None
		"""
		CEquip.set( self, attrName, value, owner )
		if "ka_count" == attrName:
			ka_count = self.query( "ka_count", 0 )
			if ka_count >= self.query( "ka_totalCount", 1 ):
				#吸收的魂魄满了
				self.onSuckKaFull()

	def onSuckKaFull( self ):
		"""
		吸收的魂魄满了
		这里可以做一些事情 如:图标发光等工作
		"""
		pass

	def isFull( self ):
		"""
		魂魄是否吸收满
		"""
		return self.query( "ka_count", 0 ) >= self.query( "ka_totalCount", 1 )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/02/21 03:14:27  kebiao
# add: isFull( self )
#
# Revision 1.1  2008/02/20 08:33:16  kebiao
# no message
#
#
