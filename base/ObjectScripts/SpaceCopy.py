# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.5 2008-04-16 05:50:45 phw Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from Space import Space

class SpaceCopy( Space ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Space.__init__( self )
		self._maxCopy = 0				# 本类型的space最多能够被创建的个数 0 代表无限

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		Space.onLoadEntityProperties_( self, section )

		# 副本专用参数( for base only )
		self.setEntityProperty( "waitingCycle",	section.readInt("waitingCycle") )	# 空转周期，空间无玩家后关闭的时间
		self.setEntityProperty( "maxPlayer",	section.readInt("maxPlayer") )		# 空间最多允许进入的人数 0 为无限制

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		Space.load( self, section )
		self._maxCopy = section.readInt("maxCopy")


	#------------------------------------------------------------------------------------------------------------------------------------

	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'dbID' : entity.databaseID, 'spaceKey': entity.databaseID }

	def onEnter( self, selfEntity, baseMailBox, params ):
		"""
		virtual method.
		玩家进入了空间
		@param baseMailbox: cell mailbox
		@type baseMailbox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		selfEntity.stopCloseCountDownTimer()			# 并且尝试停止关闭倒计时功能

	def onLeave( self, selfEntity, baseMailBox, params  ):
		"""
		virtual method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		if selfEntity.getCurrentPlayerCount() == 0 and selfEntity.waitingCycle > 0:
			selfEntity.startCloseCountDownTimer( selfEntity.waitingCycle )	# 尝试开始关闭倒计时，如果还没开始。

	def onCloseSpace( self, selfEntity ):
		"""
		virtual method.
		space生命周期结束，正在删除space,这里可以做一些准备删除时要做的事情
		"""
		pass

	def checkIntoDomainEnable( self, entity ):
		"""
		virtual method.
		检查domain的进入条件
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		"""
		return csstatus.SPACE_OK
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		队伍解散
		"""
		pass

# SpaceNormal.py
