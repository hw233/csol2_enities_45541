# -*- coding: gb18030 -*-

# $Id: CVehicleEquip.py,v 1.2 2008-08-28 08:19:34 yangkai Exp $

from CItemBase import CItemBase
from gbref import rds
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import ItemAttrClass
import TextFormatMgr
import csstatus
import Define

from VehicleHelper import isOnFlyingVehicle, isOnVehicle, isVehicleEquipUseable

class CVehicleEquip( CItemBase ):
	"""
	���װ��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def canWield( self, owner ):
		"""
		�Ƿ���װ�������װ��
		�ڿͻ���owner��role
		"""
		return isVehicleEquipUseable( self, owner ) == csstatus.KIT_EQUIP_CAN_FIT_EQUIP

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡװ��ר��������Ϣ
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# ��������
		desExtraEffectList = attrMap["eq_extraEffect"].descriptionList( self, reference )
		desExtraEffectListTemp = []
		for desExtraEffect in desExtraEffectList:
			des = PL_Font.getSource(desExtraEffect[0] + desExtraEffect[1] , fc = ( 0, 255, 0 ) )
			desExtraEffectListTemp.append( [ des ] )
		self.desFrame.SetDesSeveral( "eq_extraEffect", desExtraEffectListTemp)
		# �ȼ�����
		desReqlevel = attrMap["reqLevel"].description_vehicle( self, reference )
		level = reference.getVehicleLevel()
		if level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription( "itemreqLevel" , desReqlevel )

	def checkUseStatus( self, owner ) :
		"""
		�����Ʒ��ʹ�����
		"""
		if self.canWield( owner ) :
			return Define.ITEM_STATUS_NATURAL
		return Define.ITEM_STATUS_USELESSNESS

# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/28 08:17:43  yangkai
# no message
#
