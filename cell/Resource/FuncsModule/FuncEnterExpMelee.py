# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr

ENTERN_EXP_MELEE_MENBER_DISTANCE = 30.0
HUAN_XIN_GU_WU_BUFF				 = 299006

class FuncEnterExpMelee( Function ):
	"""
	���뾭���Ҷ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )		#����ȼ�


	def do( self, player, talkEntity = None ):
		"""
		���뾭���Ҷ�������
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
				�����Աû�н���������ġ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		if not BigWorld.globalData.has_key('AS_ExpMelee'):
			#�����Ҷ��û�п���
			player.statusMessage( csstatus.EXP_MELEE_IS_NOT_OPEN )
			return

		if self.level > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.EXP_MELEE_LEVEL_NOT_ENOUGH )
			return

		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.EXP_MELEE_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'ExpMelee_%i'%player.getTeamMailbox().id ):
			#��ҵĶ���ӵ��һ�������Ҷ�����
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_JING_YAN_LUAN_DOU ):
				player.statusMessage( csstatus.EXP_MELEE_HAS_ENTER )
				return

			player.gotoSpace('fu_ben_exp_melee', (0, 0, 0), (0, 0, 0))
			player.addActivityCount( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
			return
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			if not len(player.getAllMemberInRange( ENTERN_EXP_MELEE_MENBER_DISTANCE )) >= 3 :
				player.statusMessage( csstatus.EXP_MELEE_NOT_ENOUGH_MEMBER )
				return

			pList = player.getAllMemberInRange( ENTERN_EXP_MELEE_MENBER_DISTANCE )
			expMeleeEnterFlag = False
			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.EXP_MELEE_MEMBER_LEVEL_NOT_ENOUGH )
					return

				if i.isActivityCanNotJoin( csdefine.ACTIVITY_JING_YAN_LUAN_DOU ):
					player.statusMessage( csstatus.EXP_MELEE_MEMBER_HAS_ENTER, i.getName() )
					expMeleeEnterFlag = True

			if expMeleeEnterFlag : return

			# ������Ϊ�˴�������������
			player.setTemp( "currentSpaceName", player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			player.setTemp( "enterPosition", player.position )
			player.setTemp( "enterDirection", player.direction )

			for i in pList:
				i.addActivityCount( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
				i.gotoSpace('fu_ben_exp_melee', (0, 0, 0), (0, 0, 0))

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

