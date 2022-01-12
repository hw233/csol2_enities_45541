# -*- coding: gb18030 -*-

import BigWorld
import random
import csdefine
import csconst
import Define
import keys
import event.EventCenter as ECenter
from bwdebug import *
import weakref
from NPC import NPC
from Function import Functor
import skills
import GUIFacade
import InvoicesPackType
import Timer
from NavigateProxy import NavigateProxy
from PetNavigate import PetChaser

FOLLOW_BEHIND_DISTANCE			= 3	# �ף�������������ߵľ���
FOLLOW_DETECT_INTERVAL			= 0.5	# �룬�������ʱ����

TIME_TO_GET_INVOICE = 1.0

def calFollowPosition( srcPosition, dstPosition, distance = FOLLOW_BEHIND_DISTANCE ):
	"""
	����Դλ����Ŀ��λ����������Ŀ��λ��distanceԶ���Ǹ���

	@param dstPosition : Ŀ�굱ǰλ�ã�Vector3
	rType : ��dstPosition·��ΪFOLLOW_BEHIND_DISTANCE�׵�position��Vector3
	�����srcPosition��dstPosition�ĵ�λ�����ķ�������Ȼ���ģ
	"""
	ppDistance = srcPosition.flatDistTo( dstPosition )
	if ppDistance < distance:
		return srcPosition
	return ( ( dstPosition - srcPosition ) / ppDistance ) * ( ppDistance - distance ) + srcPosition

def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	�߻������ǣ������ǮС��1������1
	�������1����ȡ��
	"""
	if price < 1:
		return 1
	return int( price )


class EidolonChaser(PetChaser):

	def _getFollowPosition( self ):
		"""<Overriding method>
		��ȡ׷��λ�ã�С�����Ǹ���������
		"""
		target = self._followTarget()
		if target:
			return self._formatPosition(target.position, target.yaw, -self._stayRange())
		else:
			return self._consigner.position

	def _addTimer( self ):
		"""<Overriding method>
		��ʼ׷�ٺ�����timer��ͣ׷��Ŀ��
		"""
		self._cancelTimer()
		self._timer = Timer.addTimer( 0.5, 0.5, self._onTimer )

	def _onTimer( self ):
		"""<Overriding method>
		����timer�ص�
		"""
		# ���ڿͻ��˲�����С�����id����������ٶȸı�ʱ
		# �޷�ͨ��id����С���鲢֪ͨ���ٶȸı䣬������ÿ
		# һ������timer�ص�ʱ��������ٶȸı�
		self.updateSpeed(self._consigner.getSpeed())
		PetChaser._onTimer(self)


class EidolonNPC( NPC ) :
	"""
	С����NPC
	"""
	def __init__( self ) :
		"""
		"""
		NPC.__init__( self )
		self.navigator = None

		self.attrTrainInfo = {}
		self.currLearning = set()		# ��¼��ǰ����ѧϰ��skillID

		self.invoiceIndexList = []
		self.__invoiceCount = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enterWorld( self ):
		"""
		"""
		NPC.enterWorld( self )
		if self.isOwnerClient():
			self.cell.clientReady()
			self.navigator = EidolonChaser(self, NavigateProxy(self))

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		"""
		player = BigWorld.player()
		if not self.isOwnerClient() and player.getLevel() <= csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL: # �����ͻ�������ģ��
			return
		NPC.createModel( self, event )

	def leaveWorld( self ) :
		"""
		�뿪����ʱ������
		"""
		NPC.leaveWorld( self )
		self.__invoiceCount = 0
		if self.isOwnerClient():	# ��������˵�client��ִ��������Ϊ
			self.cancelFollow()
			BigWorld.player().onEidolonLeaveWorld()

	def onControlled( self, isControlled ):
		""""""
		INFO_MSG("Eidolon(%i) is controlled by client: %s"%(self.id, isControlled))
		if isControlled:
			self.initPhysics()
			self.initFollow()
		else:
			self.cancelFollow()

	def filterCreator( self ):
		"""
		template method.
		����С�����filterģ��
		"""
		return BigWorld.AvatarFilter()

	def initFollow( self ):
		"""
		��ʼ��С����ĸ���ai
		"""
		self.navigator.followEntity( BigWorld.player(), FOLLOW_BEHIND_DISTANCE, self.getSpeed() )

	def initPhysics( self ):
		# ֻ��controlledBy������ܳ�ʼ��physics����ʱ�п��ܿͻ��˵�controlledBy���û�δ��ʼ����ϣ������ʱ��ʼ�����ɹ�������followCheck����û��physics���ٴγ�ʼ��
		try:
			self.physics = keys.SIMPLE_PHYSICS
			self.physics.fall = True
			self.physics.collide = False
		except AttributeError:
			TRACE_MSG( "Only controlled entities have a 'physics' attribute,maybe controlledBy hasnot init" )

	def cancelFollow( self ):
		"""
		"""
		self.stopMove()

	def standActionOff( self ):
		self.am.matchCaps = [8]

	def standActionOn( self ):
		self.am.matchCaps = [0]

	def isOwnerClient( self ):
		"""
		�Ƿ������˵Ŀͻ���
		"""
		return BigWorld.player().id == self.ownerID

	def stopMove( self ) :
		"""
		ֹͣ�ƶ�
		"""
		self.navigator.stop()

	def getSpeed( self ):
		return BigWorld.player().move_speed * ( 1.2 )	# ������ٶȿ�һ�㣬�������

	def updateVelocity( self ) :
		"""
		���¸����ٶ�
		"""
		self.navigator.updateSpeed(self.getSpeed())

	def vipShareSwitch( self ):
		"""
		����vip����
		"""
		if self.isOwnerClient():
			self.cell.vipShareSwitch()

	def set_bornTime( self, oldValue ):
		"""
		���С�������ʱ�������С���������ٻ�ʣ����ʱ��
		"""
		pass

	# --------------------------------------------------------------------------
	# ����ѧϰ����
	# --------------------------------------------------------------------------
	def receiveTrainInfos( self, skillIDs ):
		"""
		@param skillIDs: array of int64
		"""
		#self.attrTrainIDs = set( skillIDs )
		if len(self.attrTrainInfo) != 0:  #�жϼ�����û�м��ع�
			self.attrTrainInfo = {}
			self.getSkillAndShowWindow(skillIDs)
		else:
			self.loadSkillAndShowWindow(skillIDs)

	def getSkillAndShowWindow(self, skillIDs):
		for id  in skillIDs:
			spell = skills.getSkill( id )
			name = spell.getName()
			type = 0	# ��ʱȫΪ0
			level = spell.getReqLevel()
			cost = spell.getCost()
			self.attrTrainInfo[id] = [name, type, level, cost]

		self.filterIdle()
		GUIFacade.showLearnSkillWindow( self )

	def loadSkillAndShowWindow(self, skillIDs):
		onceLoadNum = 10 			#һ���Լ��ؼ�����
		callTimer = 0.2 			#�ٴ�ִ��ʱ��

		def onSectionGetSkill():
			getIDs = []
			if len(skillIDs) > onceLoadNum:
				getIDs = skillIDs[0:onceLoadNum]
			else:
				getIDs = skillIDs

			for id  in getIDs:
				skillIDs.pop(0)
				spell = skills.getSkill( id )
				name = spell.getName()
				type = 0	# ��ʱȫΪ0
				level = spell.getReqLevel()
				cost = spell.getCost()
				self.attrTrainInfo[id] = [name, type, level, cost]

			if len(skillIDs) > 0:
				BigWorld.callback( callTimer, onSectionGetSkill )
			else:
				self.filterIdle()
				GUIFacade.showLearnSkillWindow( self )

		onSectionGetSkill()

	def train( self, player, skillID ):
		"""
		@type skillID: INT16
		"""
		if skillID not in self.attrTrainInfo:
			#ERROR_MSG( "%i not exist." % skillID )
			player.statusMessage( csstatus.SKILL_NOT_HAVE, skillID )
			return
		self.currLearning.add( skillID )

		self.cell.trainPlayer( skillID )

	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		�����ж�

		@type reason: INT
		"""
		NPC.NPC.spellInterrupted( self, skillID, reason )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		��ʽʩ�ŷ�����������ʩ��������

		@type skillID: INT
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		try:
			NPC.NPC.castSpell( self, skillID, targetObject )
		except Exception, err:
			ERROR_MSG( err )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )
			GUIFacade.onSkillLearnt( skillID )

	def filterIdle( self ):
		"""
		����û���õ� ����������������
		"""
		skillIDs = []
		for s in self.attrTrainInfo:
			if skills.getSkill( s ).islearnMax( self ):
				skillIDs.append( s )
		for s in skillIDs:
			self.attrTrainInfo.pop( s )

	def getLearnSkillIDs( self ) :
		"""
		��ȡ����ѧϰ����
		"""
		self.filterIdle()
		skillIDs = self.attrTrainInfo.keys()
		count = len( skillIDs )
		for i in xrange( 1, count ):
			for ii in xrange( i ):
				iskill = skills.getSkill( skillIDs[i] )
				iiskill = skills.getSkill( skillIDs[ii] )
				if iskill.getFirstReqLevel() < iiskill.getFirstReqLevel():
					tmp = skillIDs[i]
					skillIDs[i] = skillIDs[ii]
					skillIDs[ii] = tmp
		return skillIDs

	# --------------------------------------------------------------------------
	# ���˹���
	# --------------------------------------------------------------------------

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		����һ����Ʒ

		@param  argUid: ����Ʒ��Ψһ��ʶ��
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType���͵���Ʒʵ��
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		item.set( "price", priceCarry( item.getPrice() * self.invSellPercent ) )		# �����¼۸�
		item.set( "invoiceType", argInvoice.getItemType() )								# ��Ʒ��ʹ�ö���ֵ����hyw--08.08.11��
		item.setAmount( argInvoice.getAmount() )
		argInvoice.uid = argUid														# ��¼Ψһ��ʶ
		#self.attrInvoices[argUid] = argInvoice
		GUIFacade.onInvoiceAdded( self.id, argInvoice )

		if argUid == self.__invoiceCount :											# ��ʾ������ϣ�hyw--2008.06.16��
			self.__invoiceCount = 0

	def resetInvoices( self, space ):
		"""
		�����Ʒ�б�

		@param space: ���˵���Ʒ����
		@type  space: INT8
		"""
		#self.attrInvoices.clear()
		GUIFacade.onResetInvoices( space )

	def onBuyArrayFromCB( self, state ):
		"""
		������Ʒ���ջص�

		@param state: ����״̬��1 = �ɹ��� 0 = ʧ��
		@type  state: UINT8
		@return: ��
		"""
		#INFO_MSG( "state = %i" % state )
		GUIFacade.onSellToNPCReply( state )

	def onInvoiceLengthReceive( self, length ):
		"""
		define method
		�����Ʒ�б���
		"""
		GUIFacade.setInvoiceAmount( length )
		self.invoiceIndexList = range( 1, length + 1, 1 )
		self.__invoiceCount = length						# ������Ʒ��������hyw -- 2008.09.16��
		if length == 0:
			return
		self.requestInvoice()

	def requestInvoice( self ):
		"""
		���һ����Ʒ�б�
		"""
		length = len( self.invoiceIndexList )
		if length > 0:
			self.cell.requestInvoice( self.invoiceIndexList[0] ) #����һ����Ʒ�б� ��ʱ�� 14��
		if length > 14:
			self.invoiceIndexList = self.invoiceIndexList[14:]
			BigWorld.callback( TIME_TO_GET_INVOICE, self.requestInvoice )
		else:
			self.invoiceIndexList = []

	def isRequesting( self ) :
		"""
		�Ƿ�����������Ʒ�б�
		hyw -- 2008.09.16
		"""
		return self.__invoiceCount > 0