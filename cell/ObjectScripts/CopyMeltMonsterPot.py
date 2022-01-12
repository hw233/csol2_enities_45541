# -*- coding: gb18030 -*-
from CopyTeamTemplate import CopyTeamTemplate


class CopyMeltMonsterPot(CopyTeamTemplate):

	def __init__(self):
		CopyTeamTemplate.__init__(self)

	def onConditionChange(self, selfEntity, params):
		"""事件通知，用来作为模板事件通知的统一接口"""
		CopyTeamTemplate.onConditionChange(self, selfEntity, params)

		if "TEMPLATE_EVENT" in params:
			self.handle_template_event(selfEntity, *params["TEMPLATE_EVENT"])

	def handle_template_event(self, selfEntity, event, params):
		"""处理模板事件统一接口"""
		# 将事件参数写入TEMPLATE_EVENT_PARAMS，以使后面的事件实例
		# 可以从中获取参数
		self.getCurrentStage(selfEntity).doAllEvent(selfEntity, event, params)

	def shownDetails( self ):
		"""
		"""
		return self.extendedShownDetails()
