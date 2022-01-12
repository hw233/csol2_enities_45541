# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.9 2008-08-29 02:38:42 huangyongwei Exp $

"""
Base class for all QuestBox
QuestBox����
"""

import GUI
import Language
import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import event.EventCenter as ECenter
from gbref import rds
import Pixie
import Math
import math
import Define

class CollectPoint( NPCObject ):
	"""
	QuestBox����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		self.__canSelect = False
		self.state = 0					# �ڵ���NPCObject.enterWorld( self )ʱ����Ҫ��һ�� self.state��ֵ˵�������״̬�����state��˵������״̬�ġ�
		self._catch_particle = None		# ���ڼ�¼��֮ǰ������particles
		self.reqSle = 0
		self.sleUpMax = 0
		self.reqSkillID = 0
		self.refurbishTaskStatus()
		#self.weaponType = Define.WEAPON_TYPE_NONE
		self.setSelectable( False )

	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return
		
		NPCObject.onCacheCompleted( self )
		self.setSelectable( True )
		
		self._canSelect = self.state
		self.setVisibility( self.state )
		self.playEnterEffect( self.state )
		
	def onCollectDatas( self, skillID, sleight, sleightUpMax ):
		"""
		define method
		���ÿͻ��˲ɼ������輼�ܡ�������
		"""
		self.reqSkillID = skillID
		self.reqSle = sleight
		self.sleUpMax = sleightUpMax

	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()
	
	def refurbishTaskStatus( self ):
		"""
		����cell�����Լ�������Ŀ��״̬
		"""
		self.cell.collectStatus()
			
	def onCollectStatus( self, state ):
		"""
		define method
		����״̬�ı�ͨ��
		@param state: ֵΪTrue(��ʾ���ӿ�ѡ�� ���� False����ʾ���Ӳ���ѡ��
		"""
		self.state = state
		self.__canSelect = state
		self.setSelectState( state )
		self.setSelectable( True )

		if self.hasFlag( 0 ):
			self.setSelectable( True )
			self.setVisibility( False )
		else:
			if self.__canSelect:
				self.setSelectable( True )
				self.setVisibility( True )
				self.playEnterEffect( True )
			else:
				self.setVisibility( False )
				self.playEnterEffect( False )
		v = False
		if self.model:
			v = self.model.visible
		ECenter.fireEvent( "EVT_ON_RES_VISIBLE_STATUS", self.id, v )

	def onTargetFocus( self ):
		"""
		����ƶ���������
		"""
		if self.__canSelect:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
			NPCObject.onTargetFocus( self )
			rds.ccursor.set( "pickup" )

	def onTargetBlur( self ):
		"""
		���������ƿ�
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		NPCObject.onTargetBlur( self )
		rds.ccursor.normal()

	def set_playEffect( self, old ):
		"""
		"""
		if len( self.playEffect ):
			print "play effect"

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
		���ſͻ��˱��ֹ�Ч
		"""
		model = self.model
		if model is None: return

		if play and self._catch_particle is None:
			self._catch_particle = Pixie.create( "particles/tong_tong/diaoluowupin.xml"  )

			# ȡģ��bounding box�ĳ�������
			m1 = Math.Matrix( model.bounds )
			m2 = Math.Matrix( self.matrix )
			x = m1.get( 0, 0 ) / m2.get( 0, 0 )
			y = m1.get( 1, 1 ) / m2.get( 1, 1 )
			z = m1.get( 2, 2 ) / m2.get( 2, 2 )

			# ȡģ�ͶԽ��߳���Ϊ���ʣ����ڳ�3�������Ǹ���������
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

	def onLoseTarget( self ) :
		"""
		"""
		if BigWorld.target.entity != self:
			BigWorld.player().stopPickUpQuestBox()
			# self.abandonBoxQuestItems()
		NPCObject.onLoseTarget( self )
	
	def enterWorld( self ):
		"""
		�����ɫ����
		"""
		ECenter.fireEvent( "EVT_ON_RES_ENTER_WORLD", self )
		NPCObject.enterWorld( self )
	
	def leaveWorld( self ):
		"""
		�뿪��ɫ����
		"""
		ECenter.fireEvent( "EVT_ON_RES_LEAVE_WORLD", self )
		NPCObject.leaveWorld( self )
		
	def set_flags( self, old ):
		"""
		"""
		if self.hasFlag(0):
			self.setSelectable( False )
			self.setVisibility( False )
		else:
			self.refurbishTaskStatus()
			self.setVisibility( True )
			
	def pickUpCollectPointItems( self, itemDict ):
		"""
		define method
		ʰȡ�ɼ�����Ʒ��ֱ����ʾʰȡ����
		"""
		player = BigWorld.player()
		player.currentItemBoxID = self.id
		player.currentQuestItemBoxID = self.id
		items = []
		for index, itemID in enumerate( itemDict ):
			item = rds.itemsDict.createDynamicItem( itemID )
			if item is None: continue
			item.setAmount( itemDict[itemID] )
			items.append( {"order": index, "item": item } )
		ECenter.fireEvent( "EVT_ON_GET_COLLECT_POINT_ITEMS", items )
		
	def pickUpItemByIndex( self, index ):
		"""
		ʰȡ�ɼ�����Ʒ��������Ʒ��˳��ʰȡ
		"""
		self.cell.onPickUpItemByIndex( index )
		
	def pickUpAllItems( self ):
		"""
		"""
		pass
		
	def pickUpItemByIndexBC( self, index ):
		"""
		defined method
		ʰȡһ����Ʒ��Ļص�
		"""
		ECenter.fireEvent( "EVT_ON_PICKUP_ONE_QUEST_ITEM", index )
		
	def abandonBoxItems( self ):
		"""
		�ص�ʰȡ����ʱ��������Ʒ�б�
		Ϊ���ֽӿ�һ���Զ����ڵĽӿ�
		"""
		pass
		
	def abandonBoxQuestItems( self ):
		"""
		�ص�ʰȡ����ʱ��������Ʒ�б�
		Ϊ���ֽӿ�һ���Զ����ڵĽӿ�
		"""
		pass