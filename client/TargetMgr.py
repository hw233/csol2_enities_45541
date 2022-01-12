# -*- coding: gb18030 -*-
#
# $Id: TargetMgr.py,v 1.20 2008-07-08 09:27:59 yangkai Exp $

"""
implement target info class

2008/01/23: writen by huangyongwei
2008/12/28: modified by huangyongwei
			�� Tact.py �е�Ŀ����ز������ܣ�ȫ���Ƶ�����
			��Ŀ����صĿ�ݼ�����ȫ���ŵ�����
"""

import random
import weakref
import BigWorld
import csdefine
import csconst
import csarithmetic
import Const
import utils
import event.EventCenter as ECenter
import GUIFacade

from gbref import rds
from UnitSelect import UnitSelect
from ShortcutMgr import shortcutMgr
from Function import Functor


# --------------------------------------------------------------------
# implement target manager singleton class
# --------------------------------------------------------------------
class TargetMgr :
	__inst = None

	def __init__( self ) :
		assert TargetMgr.__inst is None
		self.__target = None
		self.__nearEnemyList = []															# �����һ������б�
		self.__nailKindnessList = []														# �����һ���Ѻ�Ŀ���б�
		self.__nearTeammateList = []														# �����һ������б�

		shortcutMgr.setHandler( "FIXED_UNBIND_TARGET", self.unbindTarget )					# ȡ��Ŀ���
		shortcutMgr.setHandler( "FIXED_CLOSE_TO_TARGET", self.__closeTarget )				# ����ָ��Ŀ��
		shortcutMgr.setHandler( "FIXED_SPELL_TARGET", self.__spellTarget )					# ֱ�Ӱ󶨲������Ҽ�ѡ�еĵ���
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_ENEMY", self.__nailEnemy )				# ���������һ������
		shortcutMgr.setHandler( "COMBAT_NAIL_FORWARD_ENEMY", self.__nailForeEnemy )			# ѡ��ǰһ������
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_KINDNESS", self.__nailKindness )			# ѡ�������һ���Ѻ�Ŀ��
		shortcutMgr.setHandler( "COMBAT_NAIL_NEAR_TEAMMATE", self.__nailTeammate )			# ѡ�����һ������
		shortcutMgr.setHandler( "COMBAT_NAIL_FORWARD_TEAMMATE", self.__nailForeTeammate )	# ѡ����һ������
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE1", self.__nailTeammate1 )				# ѡ��ڶ�������
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE2", self.__nailTeammate2 )				# ѡ�����������
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE3", self.__nailTeammate3 )				# ѡ����ĸ�����
		shortcutMgr.setHandler( "COMBAT_NAIL_TEAMMATE4", self.__nailTeammate4 )				# ѡ���һ������
		shortcutMgr.setHandler( "COMBAT_NAIL_MY_PET", self.__nailMyPet )					# ѡ���Լ��ĳ���
		shortcutMgr.setHandler( "COMBAT_NAIL_TARGET_OF_TARGET", self.__nailTargetOfTarget )	# ѡ��Ŀ���Ŀ��

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = TargetMgr()
		return SELF.__inst

	def bindTargetCheck( self, target ) :
		"""
		��Ŀ��Ϸ��Լ��
		"""
		if target is None :					# ��Ŀ��
			return False
		if not target.selectable :			# ����ѡ��Ŀ��
			return False
		if not target.getVisibility() :		# Ŀ�겻�ɼ�
			return False
		if getattr( target, "flags", 0 ) != 0 and not self.isRoleTarget( target ): 
			if target.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):								# �в�����ɫ���ѡ���ʶ
				return False
		return True

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __notifyServer( self, targetID ) :
		"""
		֪ͨ������ѡ��Ŀ��
		"""
		player = BigWorld.player()
		if hasattr( player.cell, "changeTargetID" ) :
			player.cell.changeTargetID( targetID )

	def __bindTarget( self, target ) :
		"""
		�ڲ���һ��Ŀ��
		"""
		if not self.bindTargetCheck( target ) :
			return False

		if self.isVehicleTarget( target ) :								# ���Ŀ�������
			target = target.getHorseMan()								# ���Ŀ��ת��Ϊ��������

		oldTarget = self.getTarget()									# ��¼����һ��Ŀ��
		self.__target = weakref.ref( target )							# ����Ϊ�µ�Ŀ��
		if oldTarget and oldTarget != target :							# �����һ��Ŀ�����
			oldTarget.onLoseTarget()									# �򣬴�����һ��Ŀ���ʧȥѡ�лص�
			ECenter.fireEvent( "EVT_ON_TARGET_UNBINDED", target )
		target.onBecomeTarget()											# ��������Ŀ���ѡ�лص�
		self.__notifyServer( target.id )								# ֪ͨ��������Ŀ��ı�

		if not isinstance( target.model, BigWorld.PyModelObstacle ):	# ��̬ģ�Ͳ������ѡ���Ȧ������ͻ��˻������������ʾ���� target.models[0]��yk����2008-7-8 ��
			bindTarget = target
			if hasattr( target, "emptyModel" ) and target.emptyModel:	# ������Ȧ����
				bindTarget = target.emptyModel
				texture = UnitSelect().getTexture( target )
				UnitSelect().setTargetTexture( texture )
			UnitSelect().setTarget( bindTarget )						# ��ʾ��Ȧ
		ECenter.fireEvent( "EVT_ON_TARGET_BINDED", target )

		if self.isNPCTarget( target ) :									# ���ѡ��Ŀ���� NPC
			rds.helper.courseHelper.interactive( "dianjiNPC_caozuo" )	# �򣬴�����һ�ε�� NPC ������ʾ
		elif self.isRoleTarget( target ) :								# ���ѡ�е�Ŀ���ǽ�ɫ
			rds.helper.courseHelper.interactive( "xuanzewanjia_caozuo" )# �򣬴�����һ�ε����ɫ������ʾ
		elif self.isMonsterTarget( target ) :							# ���ѡ�е�Ŀ���ǹ���
			rds.helper.courseHelper.interactive( "xuanzeguaiwu_caozuo" )# �򣬴�����һ�ε�����������ʾ
		return True


	# -------------------------------------------------
	@staticmethod
	def __isEntityInView( entID ) :
		"""
		�ж�ָ���� entity �Ƿ������������
		"""
		entity = BigWorld.entity( entID )
		if entity is None : return False
		x, y, z = utils.world2RScreen( entity.position )
		return x > -1 and x < 1 and y > -1 and y < 1

	def __bindEntityInList( self, entList, index ) :
		"""
		��ָ�� entity �б��е�ָ��������Ŀ�꣬�󶨳ɹ��򷵻� True�����򷵻� False
		"""
		if index >= len( entList ) or \
			not self.__isEntityInView( entList[index] ) :			# ����Ѿ��������ѡ�б���ָ�������еĵ����Ѿ��뿪�������Ұ
				return False
		entID = entList[index]
		return self.__bindTarget( BigWorld.entity( entID ) )


	# ----------------------------------------------------------------
	# private shortcut implementer
	# ----------------------------------------------------------------
	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_ENEMY���Զ�ѡ�������һ�����
	# -------------------------------------------------
	def __pickUpItem( self, item ) :
		"""
		���������Ʒ
		"""
		def closedTarget( success ) :										# ����������Ʒ����Ļص�
			if success : player.startPickUp( item )

		space = 3.0
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_DEAD: return
		if player.affectAfeard : return										# �����ɫ���ڿ���״̬�����������߶�
		ppos = player.position
		ipos = item.position
		dist = ppos.distTo( ipos )											# ��ɫ����Ʒ�ľ���
		if dist <= space :													# ���С�� 3 ��
			player.startPickUp( item )										# ��ֱ�Ӽ�����Ʒ
		else :
			pos = csarithmetic.getSeparatePoint3( ipos, ppos, space )
			player.moveTo( pos, closedTarget )

	def __talkWithTarget( self, target ) :
		"""
		��Ŀ��Ի�
		"""
		def clsedTarget( player, target, success ) :
			if not success : return											# ��������Ի�Ŀ��ʧ�ܣ��򷵻�
			if self.getTarget() == target :									# �����;û�ı�Ի�Ŀ��
				GUIFacade.gossipHello( target )								# ����жԻ�
				rds.helper.courseHelper.interactive( "NPCjiaohu_caozuo" )	# ��������NPC�Ի����Ĺ��̰���

		player = BigWorld.player()
		dist = player.position.distTo( target.position )
		space = csconst.COMMUNICATE_DISTANCE 								# ��Ի�Ŀ��֮��ĿɶԻ�����
		if hasattr( target, "getRoleAndNpcSpeakDistance" ) :				# add by gjx 2009-4-2
			space = target.getRoleAndNpcSpeakDistance()						# ���� -2 ��Ϊ�˷�ֹ��ɫ��NPC����ȶԻ�����Զһ����ʱ�򣬶Ի����һ���־���ʧ������>>> ȡ����2��������ЩNPC�����в�����Խ���ϰ�����2���ܻᵼ���߲���NPC��ߣ��������С��
		if dist < space :													# ����ڿɶԻ�������
			BigWorld.player().gossipVoices = 0
			GUIFacade.gossipHello( target )									# ��ֱ�ӽ��жԻ�
#			if player.soundPriority > 0: return									#��ɫ�����ȼ�����0���򲻲���Ĭ������
#			self.__playNPCVoice( target )
		else :																# ����
			dec = min( 2, space * 0.8 )
			space -= dec													# ���̸�NPC��ʵ�ʾ��룬��֤���ܵ�NPC�Ի�����֮��
			player.pursueEntity( target, space, clsedTarget )				# �ܵ�Ŀ���ǰ�ٽ��жԻ���

	def __playNPCVoice( self, target ):
		"""
		����NPC����
		"""
		if target.voiceBan:
			return
		model = target.getModel()
		if model is None:
			return
		voices = rds.npcVoice.getClickVoice( int(target.className) )
		if len( voices ) <= 0:
			return
		voice = random.choice( voices )
		rds.soundMgr.playVocality( voice, model )
		try:
			target.setVoiceDelate()
		except:
			return

	def __viewVend( self, target ) :
		"""
		�쿴��ɫ��̯��Ʒ
		"""
		def endPursue( player, target, success ) :							# ���������ص�
			if success :													# ��������ɹ�
				player.vend_buyerQueryInfo( target.id )						# ��쿴Ŀ���̯

		player = BigWorld.player()
		if player.position.flatDistTo( target.position ) > \
			csconst.COMMUNICATE_DISTANCE:									# ��������Զ�������߹�ȥ
				dec = min( 2, csconst.COMMUNICATE_DISTANCE * 0.8 )
				space = csconst.COMMUNICATE_DISTANCE - dec
				player.pursueEntity( target, space, endPursue )				# ������̯���
		else :
			player.vend_buyerQueryInfo( target.id )							# ����ڽ��������ڣ���ֱ�Ӳ쿴�Է���̯

	def __pickFruit( self, target ):
		"""
		ʰȡ������ʵ
		"""
		def closedTarget( success ) :										# ����������Ʒ����Ļص�
			if success : player.pickFruit( target.id )

		space = 3.0
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_DEAD: return
		if player.affectAfeard : return										# �����ɫ���ڿ���״̬�����������߶�
		ppos = player.position
		ipos = target.position
		dist = ppos.distTo( ipos )											# ��ɫ����Ʒ�ľ���
		if dist <= space :													# ���С�� 3 ��
			player.pickFruit( target.id )									# ��ֱ�Ӽ�����Ʒ
		else :
			pos = csarithmetic.getSeparatePoint3( ipos, ppos, space )
			player.moveTo( pos, closedTarget )

	def __closeTarget( self ) :
		"""
		ѡ��/����Ŀ��
		ע����һ�δ���ʱ���������е�Ŀ�꣬�ڶ��δ���ʱ������Ŀ��
		"""
		target = BigWorld.target.entity
		if target is None : return False

		player = BigWorld.player()
		oldTarget = self.getTarget()										# ��¼��ԭ����Ŀ��

		if self.isDropItemTarget( target ) :								# ���Ŀ���ǵ�����Ʒ
			self.__pickUpItem( target )										# �������Ʒ
		elif self.isDropBoxTarget( target ):								# ���Ŀ���ǵ�������
			self.__pickUpItem( target )										# �򣬼�����Ʒ
			self.bindTarget( target )										# �����µ�Ŀ�꣨�ʣ�Ϊʲô��Ҫ�ٴΰ�����hyw����2009.06.13��
		elif self.isCollectPointTarget( target ):							# ����ǲɼ��㣬һ��ʹ��� by ����
			self.bindTarget( target )
			self.__talkWithTarget( target )
		elif oldTarget != target :											# �����һ�ε��Ŀ��
			self.bindTarget( target )										# �򣬰��µ�Ŀ��
		elif self.isFruitTree( target ):
			self.__pickFruit( target )
		elif self.isDialogicTarget( target ) :								# ���Ŀ���ǿɶԻ���
			self.__talkWithTarget( target )									# ����Ŀ��Ի�
		elif self.isEnemyTarget( target ) :									# ����ǿɹ���Ŀ��
			if player.isPursueState():
				player.cancelAttackState()
			player.onLClickTargt()											# �򣬶�Ŀ�귢������
		elif self.isRoleTarget( target ) and \
			target.state == csdefine.ENTITY_STATE_VEND :					# ����Ǵ��ڰ�̯״̬�µĽ�ɫ�����Ǵ� Tact ��ԭ�渴�ƹ����ģ�����жϺܲ��ã�
				self.__viewVend( target )
		elif self.isDanceSeatTarget( target ):  							# ����������е���λ
			player.canGetDancePosition( target.locationIndex )
		target.onTargetClick( player )										# ���� target ������Ļص�
		return True

	# -------------------------------------------------
	# FIXED_SPELL_TARGET��ֱ�ӹ������ָ���ĵ��ˣ�
	# -------------------------------------------------
	def __spellTarget( self ) :
		"""
		ֱ�ӹ���Ŀ��
		"""
		target = BigWorld.target.entity
		player = BigWorld.player()
		if target is None : return False									# û��Ŀ��

		if self.isVehicleTarget( target ) :									# ���Ŀ�������
			target = target.getHorseMan()									# �򣬸���Ŀ��Ϊ������
		if player.queryRelation( target ) == csdefine.RELATION_ANTAGONIZE :	# �Ƿ��ǵжԹ�ϵ��Ŀ��
			self.bindTarget( target )										# ���µ�Ŀ��
			player.onRClickTargt()											# ���𹥻�
			return True
		return False

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_ENEMY���Զ�ѡ�������һ�����ˣ�
	# -------------------------------------------------
	@staticmethod
	def __isNailEnemy( enemy ) :
		"""
		�ж�ָ���ĵ����Ƿ����Զ�ѡ��ʱ����Ȥ�ĵ���
		"""
		player = BigWorld.player()
		if not TargetMgr.__isEntityInView( enemy.id ) : return False
		if not enemy.getVisibility() : return False											# Ŀ�겻�ɼ�
		if enemy.viewProjectionCull(): return False											# ���������Ұ�ü�
		if getattr( enemy, "flags", 0 ) != 0 and not TargetMgr.isRoleTarget( enemy ):
			if enemy.hasFlag(csdefine.ENTITY_FLAG_CAN_NOT_SELECTED):
				return False

		if player.state == csdefine.ENTITY_STATE_RACER and TargetMgr.isRoleTarget( enemy ):
			# ����ʱ������ʱѡ���ɫ
			return True

		if enemy.isEntityType( csdefine.ENTITY_TYPE_PET ) :									# �ж��Ƿ�Ϊ���
			enemy = enemy.getOwner()														# �ǵĻ���Ŀ��ת�Ӹ��������������ж�
			if enemy is None : return False 												# �Ҳ����ó�������� ����ѡ��

		if player.qieCuoState == csdefine.QIECUO_READY or player.qieCuoState == csdefine.QIECUO_FIRE:  #�����д�״ֻ̬TAB�Է���һ����
			if hasattr( enemy, "id" ) and player.qieCuoTargetID == enemy.id:
				return True
			else:
				return False

		if not ( player.canPk( enemy ) or TargetMgr.isMonsterTarget( enemy ) ):
			return False

		return TargetMgr.isEnemyTarget( enemy )

	def __nailEnemy( self ) :
		"""
		�������������һ������
		"""
		player = BigWorld.player()
		isNewList = False														# ��¼�Ƿ������������ĺ�ѡ�б�
		if len( self.__nearEnemyList ) == 0 :
			enemys = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, self.__isNailEnemy )
			self.__nearEnemyList = [ent.id for ent in enemys]
			isNewList = True
		ecount = len( self.__nearEnemyList )									# ��ѡ�б��е��˵�����
		if ecount == 0 : return													# ���û�к�ѡ���ˣ��򷵻�

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nearEnemyList :							# �����ѡ�б��������ɵ� ���� �����ǰû��ѡ��Ŀ�� ���� ��ǰĿ�겻��ѡ���б���
				if not self.__bindEntityInList( self.__nearEnemyList, 0 ) :		# �򣬰��б��еĵ�һ��
					self.__nearEnemyList = []									# ����պ�ѡ�б�
					self.__nailEnemy()											# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩
		else :																	# �����ǰѡ��Ŀ���ں�ѡ�б���
			index = self.__nearEnemyList.index( currTarget.id )					# �򣬼��㵱ǰĿ���ں�ѡ�б��е�λ��
			if not self.__bindEntityInList( self.__nearEnemyList, index + 1 ) :	# ��ѡ����һ��Ŀ��
				self.__nearEnemyList = []										# ����պ�ѡ�б�
				self.__nailEnemy()												# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩

	# -------------------------------------------------
	# COMBAT_NAIL_FORWARD_ENEMY���Զ�ѡ��ǰһ�����ˣ�
	# -------------------------------------------------
	def __nailForeEnemy( self ) :
		"""
		ѡ��Ŀ���б���ǰһ������
		"""
		target = self.getTarget()
		if target is None : return													# �����ǰû��Ŀ�꣬��û��ǰһ������
		if target.id not in self.__nearEnemyList : return							# ��ǰĿ�겻�ں�ѡ�б��У�����ζ�ŵ�ǰ�ĺ�ѡ�б��Ѿ��ϵ�
		idx = self.__nearEnemyList.index( target.id ) - 1							# ��ǰĿ���ں�ѡ�б��е�λ��
		if idx <= 0 : return														# ��ǰĿ���Ѿ�����ǰ��һ��
		targetID = self.__nearEnemyList[idx]
		target = BigWorld.entity( targetID )
		self.__bindTarget( target )

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_KINDNESS��ѡ�������һ�� NPC��
	# -------------------------------------------------
	def __nailKindness( self ) :
		"""
		ѡ�������һ�� NPC
		"""
		player = BigWorld.player()
		isNewList = False															# ��¼�Ƿ������������ĺ�ѡ�б�
		if len( self.__nailKindnessList ) == 0 :
			verifier = lambda ent : self.isKindlyTarget( ent ) and ent.getVisibility()
			enemys = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, verifier )
			self.__nailKindnessList = [ent.id for ent in enemys]
			isNewList = True
		ecount = len( self.__nailKindnessList )										# ��ѡ�б��е��˵�����
		if ecount == 0 : return														# ���û�к�ѡ���ˣ��򷵻�

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nailKindnessList :							# �����ѡ�б��������ɵ� ���� �����ǰû��ѡ��Ŀ�� ���� ��ǰĿ�겻��ѡ���б���
				if not self.__bindEntityInList( self.__nailKindnessList, 0 ) :		# �򣬰��б��еĵ�һ��
					self.__nailKindnessList = []									# ����պ�ѡ�б�
					self.__nailEnemy()												# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩
		else :																		# �����ǰѡ��Ŀ���ں�ѡ�б���
			index = self.__nailKindnessList.index( currTarget.id )					# �򣬼��㵱ǰĿ���ں�ѡ�б��е�λ��
			if not self.__bindEntityInList( self.__nailKindnessList, index + 1 ) :	# ��ѡ����һ��Ŀ��
				self.__nailKindnessList = []										# ����պ�ѡ�б�
				self.__nailEnemy()													# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩

	# -------------------------------------------------
	# COMBAT_NAIL_NEAR_TEAMMATE���Զ�ѡ�����һ�����ѣ�
	# -------------------------------------------------
	def __nailTeammate( self ) :
		"""
		ѡ�����һ������
		"""
		player = BigWorld.player()
		isNewList = False															# ��¼�Ƿ������������ĺ�ѡ�б�
		if len( self.__nearTeammateList ) == 0 :
			verifier = lambda ent : self.isTeammateTarget( ent ) and \
				ent != player and ent.getVisibility()
			teammates = player.entitiesInRange( csconst.ROLE_AOI_RADIUS, verifier )
			self.__nearTeammateList = [ent.id for ent in teammates]
			isNewList = True
		ecount = len( self.__nearTeammateList )										# ��ѡ�б��е��˵�����
		if ecount == 0 : return														# ���û�к�ѡ���ˣ��򷵻�

		currTarget = self.getTarget()
		if isNewList or not currTarget or \
			currTarget.id not in self.__nearTeammateList :							# �����ѡ�б��������ɵ� ���� �����ǰû��ѡ��Ŀ�� ���� ��ǰĿ�겻��ѡ���б���
				if not self.__bindEntityInList( self.__nearTeammateList, 0 ) :		# �򣬰��б��еĵ�һ��
					self.__nearTeammateList = []									# ����պ�ѡ�б�
					self.__nailEnemy()												# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩
		else :																		# �����ǰѡ��Ŀ���ں�ѡ�б���
			index = self.__nearTeammateList.index( currTarget.id )					# �򣬼��㵱ǰĿ���ں�ѡ�б��е�λ��
			if not self.__bindEntityInList( self.__nearTeammateList, index + 1 ) :	# ��ѡ����һ��Ŀ��
				self.__nearTeammateList = []										# ����պ�ѡ�б�
				self.__nailEnemy()													# ������ˢ���б�ע�⣺���ﲻ��������ݹ飩

	# -------------------------------------------------
	# COMBAT_NAIL_FORWARD_TEAMMATE���Զ�ѡ��ǰһ�����ˣ�
	# -------------------------------------------------
	def __nailForeTeammate( self ) :
		"""
		ѡ��Ŀ���б���ǰһ������
		"""
		target = self.getTarget()
		if target is None : return
		if target.id not in self.__nearTeammateList : return
		idx = self.__nearTeammateList.index( target.id ) - 1
		if idx <= 0 : return
		targetID = self.__nearTeammateList[idx]
		target = BigWorld.entity( targetID )
		self.__bindTarget( target )

	# -------------------------------------------------
	# COMBAT_NAIL_TEAMMATE...��������ѡ����ѣ�
	# -------------------------------------------------
	def __nailTeammate1( self ) :
		"""
		ѡ���һ������
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) == 0 : return
		teammate = BigWorld.entity( ids[0] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate2( self ) :
		"""
		ѡ��ڶ�������
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 2 : return
		teammate = BigWorld.entity( ids[1] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate3( self ) :
		"""
		ѡ�����������
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 3 : return
		teammate = BigWorld.entity( ids[2] )
		if not teammate : return
		self.bindTarget( teammate )

	def __nailTeammate4( self ) :
		"""
		ѡ����ĸ�����
		"""
		player = BigWorld.player()
		ids = player.teamMember.keys()
		if player.id in ids :
			ids.remove( player.id )
		if len( ids ) < 4 : return
		teammate = BigWorld.entity( ids[3] )
		if not teammate : return
		self.bindTarget( teammate )

	# -------------------------------------------------
	# COMBAT_NAIL_MY_PET��ѡ���Լ��ĳ��
	# -------------------------------------------------
	def __nailMyPet( self ) :
		"""
		ѡ���Լ��ĳ���
		"""
		pet = BigWorld.player().pcg_getActPet()
		if pet is None : return
		self.bindTarget( pet )

	# -------------------------------------------------
	# COMBAT_NAIL_TARGET_OF_TARGET��ѡ��ǰĿ���Ŀ�꣩
	# -------------------------------------------------
	def __nailTargetOfTarget( self ) :
		"""
		ѡ��ǰĿ���Ŀ��
		"""
		player = BigWorld.player()
		target = player.targetEntity
		if target is None : return											# ���û��Ŀ��
		if not hasattr( target, "targetID" ) : return						# Ŀ��û��Ŀ������
		targetOfTarget = BigWorld.entities.get( target.targetID, None )		# ��ȡĿ���Ŀ��
		if targetOfTarget is None : return									# ���Ŀ��û��Ŀ�꣬����
		if targetOfTarget == target : return								# ���Ŀ���Ŀ�����Լ�������
		self.bindTarget( targetOfTarget )									# ��Ŀ��Ϊ��ǰĿ���Ŀ��


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getTarget( self ) :
		"""
		��ȡ��ǰ�󶨵�Ŀ�� entity
		"""
		target = None
		if self.__target : target = self.__target()
		if target is not None and not target.inWorld :
			self.__target = None
			return None
		return target

	def bindTarget( self, entity ) :
		"""
		��һ��Ŀ�� entity
		"""
		if not rds.statusMgr.isInWorld() : return
		assert entity is not None
		if self.__bindTarget( entity ) :
			self.__nearEnemyList = []
			self.__nailKindnessList = []
			self.__nearTeammateList = []

	def unbindTarget( self, entity = None ) :
		"""
		�������� entity Ϊ None����ȥ����ǰĿ�꣬�����ǰ�󶨵�Ŀ���봫���Ŀ�겻һ�£������κ�����
		"""
		if not rds.statusMgr.isInWorld() : return False
		if self.getTarget() == None:
			return False
		if entity is None or entity == self.getTarget() :
			if self.getTarget():
				self.getTarget().onLoseTarget()
			self.__target = None
			self.__notifyServer( 0 )
			UnitSelect().detachTarget()
			ECenter.fireEvent( "EVT_ON_TARGET_UNBINDED", entity )
			self.__nearEnemyList = []
			self.__nailKindnessList = []
			self.__nearTeammateList = []
			return True
		return False

	def talkWithTarget( self, target ):
		"""
		���ô˷�������ѶԻ�Ŀ���Ϊ��ǰĿ��
		"""
		if target is None: return
		self.bindTarget( target )							# ��Ϊ��ǰĿ��
		self.__talkWithTarget( target )

	# -------------------------------------------------
	@staticmethod
	def isRoleTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǽ�ɫ
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_ROLE )

	@staticmethod
	def isPetTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǳ���
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_PET )

	@staticmethod
	def isMonsterTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǹ���
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.utype in Const.ATTACK_MOSNTER_LIST

	@staticmethod
	def isNPCTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��� NPC
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_NPC )

	@staticmethod
	def isDropItemTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǵ�����Ʒ
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_DROPPED_ITEM )

	@staticmethod
	def isDropBoxTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǵ�����Ʒ
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_DROPPED_BOX ) or target.isEntityType( csdefine.ENTITY_TYPE_MONSTER_ATTACK_BOX )

	@staticmethod
	def isVehicleTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǵ�����Ʒ
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE )

	@staticmethod
	def isDanceSeatTarget( target ):
		"""
		�ж�ָ��Ŀ���Ƿ�����������λ
		"""
		return target.__class__.__name__ == "DanceSeat"

	# ---------------------------------------
	@staticmethod
	def isTeammateTarget( target ) :
		"""
		�ж�ָ����Ŀ���Ƿ��Ƕ���
		"""
		return BigWorld.player().isTeamMember( target.id )

	@staticmethod
	def isEnemyTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǵж�Ŀ��
		"""
		# ���ѡ��Ŀ������� ��ת��Ϊ���� by����
		# ��ֹ���ͻ�ȡ�ϳ���ͻȻ�Ŀ����ͣ������ĳЩ������ʧ��
		try:
			if target.getEntityType() == csdefine.ENTITY_TYPE_VEHICLE:					# ���Ŀ�������
				target = target.getHorseMan()
		except:
			return False
		return BigWorld.player().queryRelation( target ) == csdefine.RELATION_ANTAGONIZE

	@staticmethod
	def isKindlyTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ����Ѻ�Ŀ��
		"""
		if TargetMgr.isNPCTarget( target ) :
			return True
		elif TargetMgr.isRoleTarget( target ) or \
			TargetMgr.isPetTarget( target ) :
				return BigWorld.player().queryRelation( target ) == csdefine.RELATION_NEUTRALLY
		return False

	@staticmethod
	def isDialogicTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǿɶԻ�Ŀ��
		"""
		if TargetMgr.isRoleTarget( target ):
			return False
		return target.hasFlag( csdefine.ENTITY_FLAG_SPEAKER )


	@staticmethod
	def isSelfDartTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǽ�ɫ
		"""
		if not hasattr( target, "isEntityType" ) : return False
		return target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and ( target.ownerID == BigWorld.player().id )

	@staticmethod
	def isCollectPointTarget( target ) :
		"""
		�ж�ָ��Ŀ���Ƿ��ǲɼ��� by ����
		"""
		return target.getEntityType() == csdefine.ENTITY_TYPE_COLLECT_POINT

	@staticmethod
	def isFruitTree( target ):
		"""
		Ŀ���Ƿ���������
		"""
		return target.getEntityType() == csdefine.ENTITY_TYPE_FRUITTREE

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
targetMgr = TargetMgr.instance()
