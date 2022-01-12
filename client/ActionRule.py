# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from gbref import rds
from Function import Functor

class ActionRule:
	"""
	�������Ź������
	"""
	def __init__( self ):
		"""
		"""
		self.currActionNames = []

	def getActionNames( self ):
		"""
		���ص�ǰ���Ŷ����б�
		"""
		return self.currActionNames

	def isActionning( self ):
		"""
		��ǰ�Ƿ��ڲ��Ŷ���
		"""
		return len( self.currActionNames ) > 0

	def checkActionRule( self, actionNames ):
		"""
		��鶯���б��Ƿ���ϲ��Ź���
		param actionName	: �������б�
		type actionName		: list of string
		return				: Bool
		"""
		if len( actionNames ) == 0: return
		# �õ����ڲ��ŵĶ����б���������ȼ�
		gradeMax = -1
		for actionName in self.currActionNames:
			grade = rds.spellEffect.getActionGrade( actionName )
			if grade > gradeMax:
				 gradeMax = grade

		# ��Ҫ���ŵĶ����б�����
		# ֻҪ��һ�����ȼ��ȵ�ǰֵ�����ⲻͨ��
		for actionName in actionNames:
			grade = rds.spellEffect.getActionGrade( actionName )
			if grade < gradeMax:
				return False

		return True

	def playActions( self, model, actionNames, functor ):
		"""
		���Ŷ���
		param actionName	: �������б�
		type actionName		: list of string
		param functor		: �ص�����
		type functor		: None
		return				: Bool
		"""
		if len( actionNames ) == 0: return
		if not self.checkActionRule( actionNames ): return False

		self.currActionNames = actionNames
		count = len( actionNames )
		if count == 1:
			rds.actionMgr.playAction( model, actionNames[0], callback = functor )
		elif count > 1:
			funcs = []
			funcs.extend( [None] * ( count - 1 ) )
			funcs.extend( [functor] )
			rds.actionMgr.playActions( model, actionNames, callbacks = funcs )
		return True

	def onActionOver( self, actionNames ):
		"""
		�������Ž���
		param actionNames	: �������б�
		type actionNames	: list of string
		"""
		if actionNames == self.currActionNames:
			self.currActionNames = []
