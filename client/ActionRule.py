# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from gbref import rds
from Function import Functor

class ActionRule:
	"""
	动作播放规则管理
	"""
	def __init__( self ):
		"""
		"""
		self.currActionNames = []

	def getActionNames( self ):
		"""
		返回当前播放动作列表
		"""
		return self.currActionNames

	def isActionning( self ):
		"""
		当前是否在播放动作
		"""
		return len( self.currActionNames ) > 0

	def checkActionRule( self, actionNames ):
		"""
		检查动作列表是否符合播放规则
		param actionName	: 动作名列表
		type actionName		: list of string
		return				: Bool
		"""
		if len( actionNames ) == 0: return
		# 得到正在播放的动作列表中最高优先级
		gradeMax = -1
		for actionName in self.currActionNames:
			grade = rds.spellEffect.getActionGrade( actionName )
			if grade > gradeMax:
				 gradeMax = grade

		# 将要播放的动作列表里面
		# 只要有一个优先级比当前值低则检测不通过
		for actionName in actionNames:
			grade = rds.spellEffect.getActionGrade( actionName )
			if grade < gradeMax:
				return False

		return True

	def playActions( self, model, actionNames, functor ):
		"""
		播放动作
		param actionName	: 动作名列表
		type actionName		: list of string
		param functor		: 回调函数
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
		动作播放结束
		param actionNames	: 动作名列表
		type actionNames	: list of string
		"""
		if actionNames == self.currActionNames:
			self.currActionNames = []
