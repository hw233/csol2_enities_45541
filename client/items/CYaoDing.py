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
	灵药鼑类基础模块
	"""
	def __init__( self, srcData ):
		"""
		初始化
		"""
		CItemBase.__init__( self, srcData )
		self.targetID = 0

	def checkItem( self, item, owner, target ):
		"""
		检查物品技能是否可用
		@type  item : ITEM
		@param item : 要检查的物品
		"""
		if item.isFrozen():	#冻结不能使用
			return False
		if owner.level < item.getReqLevel():
			return False	# 不允许使用
		skillID = item.query("spell")
		if skillID == None:
			return False
		sk = skills.getSkill( skillID )
		target = sk.getCastObject().convertCastObject( owner, target )
		state = sk.useableCheck( owner, SkillTargetObjImpl.createTargetObjEntity(target) )
		if state == csstatus.SKILL_GO_ON:
			if target is not None:	# 在这里存储目标的ID,这种做法非常奇怪,但是因此不必再单独计算一次,而且在这里记录总是能正确的获得ID
				self.targetID = target.id
			else:
				self.targetID = 0
			return True
		return False

	def getUsedItemOrder( self, owner, target ):
		"""
		获取该药鼑目前找到的需要被使用物品的位置
		@RETURN  : int 被使用物品的ORDERID
		"""
		kitbagOrders = owner.getRoleKitBagOrders()
		self.targetID = 0		#初始化下数据
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
		获取施放的对象的ID(因为施放的目标可能是宠物，物品的使用对象和技能是一致的)
		"""
		return self.targetID