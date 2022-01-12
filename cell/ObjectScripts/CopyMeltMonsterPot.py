# -*- coding: gb18030 -*-
from CopyTeamTemplate import CopyTeamTemplate


class CopyMeltMonsterPot(CopyTeamTemplate):

	def __init__(self):
		CopyTeamTemplate.__init__(self)

	def onConditionChange(self, selfEntity, params):
		"""�¼�֪ͨ��������Ϊģ���¼�֪ͨ��ͳһ�ӿ�"""
		CopyTeamTemplate.onConditionChange(self, selfEntity, params)

		if "TEMPLATE_EVENT" in params:
			self.handle_template_event(selfEntity, *params["TEMPLATE_EVENT"])

	def handle_template_event(self, selfEntity, event, params):
		"""����ģ���¼�ͳһ�ӿ�"""
		# ���¼�����д��TEMPLATE_EVENT_PARAMS����ʹ������¼�ʵ��
		# ���Դ��л�ȡ����
		self.getCurrentStage(selfEntity).doAllEvent(selfEntity, event, params)

	def shownDetails( self ):
		"""
		"""
		return self.extendedShownDetails()
