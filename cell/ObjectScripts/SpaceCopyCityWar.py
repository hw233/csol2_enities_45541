# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.2 2008-08-28 00:52:47 kebiao Exp $

"""
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csdefine
import random
import time
import csconst
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.SkillLoader import g_skills

WAR_TIMER_CHECK_OVER 	 = 100	# ���ս���Ƿ����
WAR_TIMER_QUEST			 = 104	# ս�����񷢷�
WAR_TIMER_CHILD_MONSTER	 = 105	# ս��С��ˢ��

BOSS_NAME = { False : cschannel_msgs.TONGCITYWAR_SHOU_FANG_JIANG_LING, True : cschannel_msgs.TONGCITYWAR_GONG_FANG_JIANG_LING }

class SpaceCopyCityWar( SpaceCopy ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		# ս�����伶��
		self.roomLevel = section[ "Space" ][ "roomLevel" ].asInt
		self.roomName  = section[ "Space" ][ "roomName" ].asString
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt

		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )

		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )

		if self.roomLevel == 1:
			data = section[ "Space" ][ "defend_playerEnterPoint" ]
			pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
			self.defend_playerEnterPoint = ( pos, direction )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		# ����ȼ�1��Ϊ��������
		if self.roomLevel > 0:
			self.initFinal( selfEntity )

	def initFinal( self, selfEntity ):
		# ������ʼ��
		if not selfEntity.params.has_key( "defend" ):
			return
		pass

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'tongDBID' : entity.tong_dbID, "ename" : entity.getName(), "dbid" : entity.databaseID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		packDict = SpaceCopy.packedSpaceDataOnLeave( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		buff = g_skills[ 122155001 ].getBuffLink( 0 ).getBuff()	# ս������ͷ�buff
		if entity.tong_grade <= 0 or entity.tong_dbID <= 0:
			return csstatus.SPACE_MISS_NOTTONG
		elif entity.level < self.enterLimitLevel:
			return csstatus.FAMILY_NO_WAR_LEVEL
		elif len( entity.findBuffsByBuffID( buff.getBuffID() ) ) > 0:
			return csstatus.TONG_CITY_WAR_ESCAPE
		return csstatus.SPACE_OK

	def getAllSpaceEntities( self, selfEntity ):
		"""
		16:41 2011-3-3 by wsf
		����ڽű���ʹ�������ڡ�for entity in BigWorld.entities.values(): ...���Ĵ��룬���������һ���ĸ��ʣ�ͨ���Ƿ�����Խæ����Խ�ߣ���崻���
		������������Դ��ڣ���bigworld�Ļ���˵��Ϊ��Ч�ʵ�ԭ�򣬲�������������ʹ�ã�Ҳ�������޸�������⡣
		��ǰ��д����ս����ʱ�䲻��������Ҳ����ʱ������ʱ�����������������⣬ʹ��entitiesInRangeExt������һ����Χ��entity���豣֤�˷�Χ>=��ǰ�������
		"""
		return selfEntity.entitiesInRangeExt( 800, None, selfEntity.position )

	def kickAllPlayer( self, selfEntity ):
		"""
		��������������߳�
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].tong_onCityWarOver()
			else:
				mailbox.cell.tong_onCityWarOver()

	def findBossID( self, selfEntity ):
		"""
		Ѱ�Ҹ�������ط�BOSSID
		���Ǽ��踱����ͬһ��cell
		"""
		for e in self.getAllSpaceEntities( selfEntity ):
			if e.spaceID == selfEntity.spaceID and e.__class__.__name__ == "BossCityWar":
				return e.id
		return 0

	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		if userArg == WAR_TIMER_CHECK_OVER:
			if selfEntity.isOverCityWar():
				self.spellCommonBuffAllPlayer( selfEntity, 122156002 )
				selfEntity.cancel( id )
				self.kickAllPlayer( selfEntity )
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )

	def onCityWarMemberLeave( self, selfEntity, memberID ):
		"""
		�������г�Ա���˳����߳����� ������������Ҫ�жϸ������Ƿ��иó�Ա
		��� �� ���������ȥ �ڸ������ǲ������ɢ�� ���Բ��ᵣ�Ľ�ɢ����
		"""
		for mailbox in selfEntity._players:
			if memberID == mailbox.id:	# ��Ȼ�����ǰ�������  ��ô��Ӧ�÷��س��и����
				player = self.getMBEntity( mailbox )
				player.tong_leaveCityWar()

	def getMBEntity( self, baseMailbox ):
		"""
		ͨ��mailboxת����һ��entity
		"""
		e = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			e = BigWorld.entities[ baseMailbox.id  ]
		return e

	def isRightBossLive( self, selfEntity ):
		"""
		�Ƿ��Ƿ��ط�boss����
		"""
		return selfEntity.queryTemp( "currentBossIsRight", False )

	def setBossLive( self, selfEntity, isRight ):
		selfEntity.setTemp( "currentBossIsRight", isRight )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = self.getMBEntity( baseMailbox )
		player.setTemp( "lastPkMode", player.pkMode )
		player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )	# ǿ����ҽ�����pk ״̬
		player.lockPkMode()														# ����pkģʽ����������

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onLeaveCityWarSpace()
		player = self.getMBEntity( baseMailbox )
		player.unLockPkMode()		# ����pkģʽ
		player.setSysPKMode( 0 )	# ���Ĭ��pkMode

		if not selfEntity.isOverCityWar():	# ���ս��û�н���ʱ�뿪�����ϳͷ�buff��2�����ڲ������ٽ���
			player.spellTarget( 122155001, player.id )

	def onBossDied( self, selfEntity ):
		"""
		ս�� �������ͳ˧����
		"""
		if selfEntity.isOverCityWar():
			return

		# ͳ˧��������
		selfEntity.setTemp( "isBossDie", True )
		selfEntity.base.closeCityWarRoom()
		self.spellCommonBuffAllPlayer( selfEntity, 122156002 )

	def closeCityWarRoom( self, selfEntity ):
		"""
		��ǰ������ĳ��ս�� ��tongmanager �ر����з���
		����������ط�ͳ˧��ǰ������
		"""
		selfEntity.setTemp( "isCurrentCityWarOver", True )
		self.kickAllPlayer( selfEntity )
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )

	def spellCommonBuffAllPlayer( self, selfEntity, skillID ):
		"""
		��������ʩ�ű�ս���ڵĹ���BUFFЧ��
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].spellTarget( skillID, mailbox.id )
			else:
				mailbox.cell.spellTarget( skillID, mailbox.id )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		DEBUG_MSG( "Role %i kill a enemy." % role.id )
		# ɱ�����Ҳ����������ʷǳ�С�����Ժ�����μ�¼
		if not killer:
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity

		if killer.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ):
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.belong, 0, role.tong_dbID, role.databaseID )
		else:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.tong_dbID, killer.databaseID, role.tong_dbID, role.databaseID )