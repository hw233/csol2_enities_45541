# -*- coding: gb18030 -*-

# $Id: CYaoDing.py

from CItemBase import CItemBase
from bwdebug import *
import SkillTargetObjImpl
import skills
import BigWorld
import csstatus

class CYaoDing(CItemBase):
	"""
	��ҩ�������ģ��
	"""
	def __init__( self, srcData ):
		"""
		��ʼ��
		"""
		CItemBase.__init__( self, srcData )
		self.targetID = 0

	def checkItem( self, item, owner, target ):
		"""
		�����Ʒ�����Ƿ����
		@type  item : ITEM
		@param item : Ҫ������Ʒ
		"""
		if item.isFrozen():	#���᲻��ʹ��
			return False
		if owner.level < item.getReqLevel():
			return False	# ������ʹ��
		skillID = item.query("spell")
		if skillID == None:
			return False
		sk = skills.getSkill( skillID )
		target = sk.getCastObject().convertCastObject( owner, target )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		if state == csstatus.SKILL_GO_ON:
			if target is not None:	# ������洢Ŀ���ID,���������ǳ����,������˲����ٵ�������һ��,�����������¼��������ȷ�Ļ��ID
				self.targetID = target.id
			else:
				self.targetID = 0
			return True
		return False

	def getUsedItemOrder( self, owner, target ):
		"""
		��ȡ��ҩ��Ŀǰ�ҵ�����Ҫ��ʹ����Ʒ��λ��
		@RETURN  : int ��ʹ����Ʒ��ORDERID
		"""
		kitbagOrders = owner.getRoleKitBagOrders()
		self.targetID = 0		#��ʼ��������
		itemLevel	 = 0
		itemOrder	 = -1
		for kitbagOrder in kitbagOrders:
			for item in owner.getItems(kitbagOrder):
				Reqlevel = item.getReqLevel()
				if Reqlevel >itemLevel and self.checkItem( item, owner, target ):
					itemOrder = item.getOrder()
					itemLevel = Reqlevel
		return itemOrder

	def getUsedTargetID( self ):
		"""
		��ȡʩ�ŵĶ����ID(��Ϊʩ�ŵ�Ŀ������ǳ����Ʒ��ʹ�ö���ͼ�����һ�µ�)
		"""
		return self.targetID