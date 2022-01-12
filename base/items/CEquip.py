# -*- coding: gb18030 -*-

# $Id: CEquip.py,v 1.5 2008-02-19 08:28:19 yangkai Exp $

"""
װ�������ģ��
"""
import ItemTypeEnum
from CItemBase import *
from bwdebug import *
from ItemSystemExp import EquipAttrExp
g_itemPropAttrExp = EquipAttrExp.instance()

class CEquip( CItemBase ):
	"""
	װ��������
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		
	def isEquip( self ):
		"""
		virtual method.
		�ж��Ƿ���װ��
		"""
		return True
		
	def getExtraEffect( self ):
		"""
		��ȡװ����������
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

	def createRandomEffect( self, owner = None ):
		"""
		����װ�����������
		@param owner: װ��ӵ����
		@type  owner: Entity
		@return Bool
		"""
		itemKey = self.id
		quality = self.getQuality()
		level = self.getLevel()
		type = self.getType()
		datas = {}
		if quality != ItemTypeEnum.CQT_WHITE:
			if not self.getExtraEffect():
				datas = g_itemPropAttrExp.getEquipRandomEffect( itemKey, level, type, quality )
		# ��ȡ�������ʧ��
		if not datas: return False
		randomEffect = datas["dic"]
		
		self.set( "eq_extraEffect", randomEffect, owner )
		return True

	def model( self ):
		"""
		��ȡģ�ͱ��
		"""
		try:
			modelList = self.srcData["model"].split(";")
			model = modelList[0]
			if self.getIntensifyLevel() >= 5 and len( modelList ) > 1:
				model = modelList[1] if modelList[1] else model
			if self.getIntensifyLevel() >= 8 and len( modelList ) > 2 :
				model = modelList[2] if modelList[2] else model
			return int ( model )
		except:
			return 0

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return INT32
		"""
		raise AssertionError, "I can't do this!"

	def getIntensifyLevel( self ):
		"""
		��ȡװ��ǿ���ȼ�
		"""
		return self.query( "eq_intensifyLevel", 0 )

	def getBjExtraEffectCount( self ):
		"""
		��ȡ��ʯ��Ƕ����
		"""
		return len( self.getBjExtraEffect() )

	def getBjExtraEffect( self ):
		"""
		��ȡ��ʯ��������
		"""
		return self.query( "bj_extraEffect", [] )


### end of class: CEquip ###


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/11/24 02:59:16  yangkai
# ��Ʒϵͳ���������Ը���
# ��ǰ�;ö�"endure" -- > "eq_hadriness"
# ����;ö�"currEndureLimit" --> "eq_hardinessLimit"
# ����;ö�����"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.3  2007/08/15 07:09:49  yangkai
# �޸�װ������
# "maxEndure"----> "currEndureLimit" // ��ǰ�;ö�����
# �������� "maxEndureLimit" // ����;ö�����
#
# Revision 1.2  2006/08/11 02:58:48  phw
# no message
#
# Revision 1.1  2006/08/09 08:24:17  phw
# no message
#
#
