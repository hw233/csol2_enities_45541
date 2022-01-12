# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.9 2008-08-29 02:38:42 huangyongwei Exp $

"""
Base class for all QuestBox
QuestBox基类
"""

import GUI
import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
import csdefine
import event.EventCenter as ECenter
from gbref import rds
import Pixie
import Math
import math
import Define

class QuestBox( NPCObject, CombatUnit ):
	"""
	QuestBox基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )
		CombatUnit.__init__( self )
		self.setSelectable( False )
		self.__canSelect = False
		self.state = 0					# 在调用NPCObject.enterWorld( self )时，需要有一个 self.state的值说明进入的状态。这个state是说明动作状态的。
		self._catch_particle = None		# 用于记录当之前创建的particles
		self.weaponType = Define.WEAPON_TYPE_NONE
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]

	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		
		# 向服务器请求更新任务状态
		self.refurbishTaskStatus()
		NPCObject.onCacheCompleted( self )
		self.fadeInModel()

	def refurbishTaskStatus(self):
		"""
		请求cell更新自己的任务目标状态
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			self.cell.taskStatus()

	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()

	def onTaskStatus( self, state ):
		"""
		define method
		任务状态改变通告
		@param state: 值为True(表示箱子可选） 或者 False（表示箱子不可选）
		"""
		self.setSelectState( state )


		if self.hasFlag( 0 ):
			self.setSelectable( False )
			self.setVisibility( False )
		else:
			if self.__canSelect:
				self.setSelectable( True )
				self.setVisibility( True )
				self.playEnterEffect( True )
			else:
				self.setVisibility( True )
				self.playEnterEffect( False )

		ECenter.fireEvent( "EVT_ON_BOX_QUEST_INDEX_TASK_STATE_CHANGED", self, state )


	def onTargetFocus( self ):
		"""
		鼠标移动到箱子上
		"""
		if self.__canSelect:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
			NPCObject.onTargetFocus( self )
			rds.ccursor.set( "pickup" )				# modified by hyw( 2008.08.29 )

	def onTargetBlur( self ):
		"""
		鼠标从箱子移开
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		NPCObject.onTargetBlur( self )
		rds.ccursor.normal()						# modified by hyw( 2008.08.29 )

	def set_playEffect( self, old ):
		"""
		"""
		if len( self.playEffect ):
			print "phw: play effect in here."

	def onBecomeTarget( self ) :
		"""
		"""
		if self.__canSelect:
			NPCObject.onBecomeTarget( self )

	def canSelect( self ):
		"""
		"""
		return self.__canSelect

	def setSelectState( self, state ):
		"""
		"""
		self.__canSelect = state
		if not state:
			self.setSelectable( False )


	def playEnterEffect( self, play = False ):
		"""
		播放客户端表现光效
		"""
		model = self.model
		if model is None: return

		if play and self._catch_particle is None:
			self._catch_particle = Pixie.create( "particles/tong_tong/diaoluowupin.xml"  )

			# 取模型bounding box的长、宽、高
			m1 = Math.Matrix( model.bounds )
			m2 = Math.Matrix( self.matrix )
			x = m1.get( 0, 0 ) / m2.get( 0, 0 )
			y = m1.get( 1, 1 ) / m2.get( 1, 1 )
			z = m1.get( 2, 2 ) / m2.get( 2, 2 )

			# 取模型对角线长度为倍率；关于除3，仅仅是个参数而已
			scale = math.sqrt( x ** 2 + y ** 2 + z ** 2	) / 3 * model.scale.y

			if scale < 0.6: scale = 0.6
			if scale > 3.0: scale = 3.0
			if scale != 1.0:
				for i in xrange( self._catch_particle.nSystems() ):
					system = self._catch_particle.system( i )
					scalar_actions = [action for action in system.actions if action.typeID == Define.PSA_SCALAR_TYPE_ID]
					for scalar_action in scalar_actions:
						scalar_action.size *= scale
						scalar_action.rate *= scale
					source_actions = [action for action in system.actions if action.typeID == Define.PSA_SOURCE_TYPE_ID]
					for source_action in source_actions:
						source_action.maximumSize *= scale
						source_action.minimumSize *= scale
			model.root.attach( self._catch_particle )
			self._catch_particle.force()

		if not play:
			if self._catch_particle is not None:
				model.root.detach( self._catch_particle )
				self._catch_particle = None


	def set_flags( self, old ):
		"""
		"""
		if self.hasFlag(0):
			self.setSelectable( False )
			self.setVisibility( False )
		else:
			self.refurbishTaskStatus()
			self.setVisibility( True )
		#模型碰撞标记
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.openCollide()

	def receiveQuestItems( self, itemBox ):				#[ {'order': 1, 'item':item01 }, ...]
		"""
		define method
		"""
		BigWorld.player().currentQuestItemBoxID = self.id
		ECenter.fireEvent( "EVT_ON_GET_QUEST_ITEMS", itemBox )

	def onBoxQuestItemRemove( self, index ):
		"""
		define method
		"""
		if BigWorld.player().currentQuestItemBoxID != self.id:
			return
		ECenter.fireEvent( "EVT_ON_PICKUP_ONE_QUEST_ITEM", index )


	def pickUpItemByIndex( self, index ):
		"""
		"""
		self.cell.pickQuestItem( index )


	def abandonBoxQuestItems( self ):
		"""
		"""
		self.cell.abandonBoxQuestItems()


	def onLoseTarget( self ) :
		"""
		"""
		if BigWorld.target.entity != self:
			BigWorld.player().stopPickUpQuestBox()
			self.abandonBoxQuestItems()
		NPCObject.onLoseTarget( self )

	def getWeaponType( self ):
		"""
		武器类型（场景物件是没有武器的）
		"""
		return Define.WEAPON_TYPE_NONE