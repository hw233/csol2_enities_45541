# -*- coding: gb18030 -*-

# $Id: CYaoDing.py

from CItemBase import CItemBase
import csdefine
import SkillTargetObjImpl
import BigWorld

class CYaoDing(CItemBase):
	"""
	灵药鼑类基础模块
	"""
	def __init__( self, srcData ):
		"""
		初始化
		"""
		CItemBase.__init__( self, srcData )

	def onUseOver( self, owner ):
		"""
		技能使用结束
		"""
		useDegree = self.getUseDegree()
		if useDegree == -1:
			pass
		elif useDegree > 1:
			self.set( "useDegree", useDegree - 1, owner )
		else:
			self.setAmount( self.getAmount() - 1, owner, csdefine.DELETE_ITEM_USEYAODING )
		owner.questIncreaseItemUsed( self.id )

	def checkItem( self, item ):
		"""
		查看该物品是否与该鼑的使用范围符合,该接口必须被重载
		"""
		pass

	def onUse( self, srcEntityID, item, owner, targetID ):
		"""
		灵药鼑使用物品
		"""
		if self.checkItem( item ):
			target = BigWorld.entities.get( targetID )
			if target is None:return
			targetObj = SkillTargetObjImpl.createTargetObjEntity( target )
			if owner.useItem( srcEntityID, item.uid, targetObj ):
				self.onUseOver( owner )
