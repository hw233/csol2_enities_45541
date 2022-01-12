# -*- coding: gb18030 -*-
#
# $Id: SpaceNormal.py,v 1.49 2008-08-20 01:22:17 zhangyuxing Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csconst
import time
from Resource.DialogManager import DialogManager
from bwdebug import *
from interface.GameObject import GameObject

class SpaceNormal( GameObject ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		# register to BigWorld.cellAppData
		BigWorld.cellAppData["spaceID.%i" % self.spaceID] = self.base
		
		super( SpaceNormal, self ).__init__()
		# ����ENTITY����
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_ENTITY )
		# ��¼����ʱ��
		self.createdTime = time.time()
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_KEY, self.className )
		if len(self.dirmapping):
			BigWorld.addSpaceGeometryMapping( self.spaceID, None, self.dirmapping )
		else:
			WARNING_MSG( "space %s has no geometry mapping." % (self.className) )

		# ����˰��
		if BigWorld.globalData.has_key( self.className + ".revenueRate" ):
			revenueRate = BigWorld.globalData[ self.className + ".revenueRate" ]
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE, revenueRate )

		space_type = self.getScript().getSpaceType()
		space_timeOfDay = self.getScript().getTimeOfDay()
		space_canPk = self.getScript().canPk
		space_canQieCuo = self.getScript().canQieCuo
		space_canConjureEidolon = self.getScript().canConjureEidolon
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY, space_type )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_NUMBER, self.spaceNumber )
		if space_canPk != True : # �������PK������
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTPK, 1 )
		if space_canQieCuo != True : # ��������д裬����
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTQIECUO, 1 )
		if space_canConjureEidolon != True : # ��������ٻ�С���飬����
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTCONJUREEIDOLON, 1 )
		BigWorld.setSpaceTimeOfDay( self.spaceID, space_timeOfDay, 0 )

		# ���Ƿ���Է�������space data������ͻ���ʹ��
		canFly = self.getScript().canFly
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY, str( canFly ) )

		# ���Ƿ�����ٻ��������space data������ͻ���ʹ��
		canVehicle = self.getScript().canVehicle
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CAN_VEHICLE, str( canVehicle ) )

		# ���ռ������ĶԽǶ�������space data, ����ͻ���ʹ�ã���ȻĿǰ��ʵ����û��ʹ�ã�
		minBBox = self.getScript().minBBox
		maxBBox = self.getScript().maxBBox
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MIN_BBOX, str( minBBox ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAX_BBOX, str( maxBBox ) )

		# ��ͼ������ȱ��浽space data
		deathDepth = self.getScript().deathDepth
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_DEATH_DEPTH, str( deathDepth ) )

		# ��ƽ�ھֺ���¡�ھ����ڻ��ֳ�ʼ��
		pointDict = {csdefine.ROLE_FLAG_XL_DARTING:csconst.DART_INITIAL_POINT,csdefine.ROLE_FLAG_CP_DARTING:csconst.DART_INITIAL_POINT}
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_DART_POINT, str( pointDict ) )

		# ע�����´��뵱ǰû��ʹ�ã�����ʹ�õ�����"spaceID.%i"�ķ�ʽ���棬
		#     ���´˴�����Ҫ�����Ժ��������á�
		# д��space entity�����basemailbox���ݵ�space data��,
		# �����κ�entity�������κεط��������ǰspace��basemailbox( ���۶��� )
		#BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAILBOX, cPickle.dumps( self.base, 2 ) )

		# ֪ͨbase�����spaceID
		# ����SpaceFace::cell::teleportToSpace()�ж�Ŀ���ͼ��Դ��ͼ�Ƿ���ͬһ��ͼ��
		self.base.onGetSpaceID( self.spaceID )

		self.RestoreTimeRatio()

	# Restore time ratio
	def RestoreTimeRatio(self):
		"""
         �ָ�ϵͳʱ�������������ͣϵͳʱ�������
	    """
		if self.timeon == 1: # time on ok; currently ratio = 2:24
			#BigWorld.setSpaceTimeOfDay(self.spaceID, BigWorld.time(), 12)
			pass
		elif self.timeon == 0: # else, stop time
			#BigWorld.setSpaceTimeOfDay(self.spaceID, BigWorld.time(), 0)
			pass

	# time on/off
	def switchTime(self, value):
		"""
		��/��ͣϵͳʱ��
		@param value:	��ʶ��/�ر�
		@type value:	UINT
		"""
		if value == 1 or value == 0:
			self.timeon = value
			self.RestoreTimeRatio()


	def onDestroy( self ):
		"""
		cell ��ɾ��ʱ����
		"""
		self.getScript().onSpaceDestroy( self )
		# deregister to BigWorld.cellAppData
		self.destroySpace()
		del BigWorld.cellAppData["spaceID.%i" % self.spaceID]

	def onTimer( self, id, userArg ):
		"""
		���ǵײ��onTimer()�������
		"""
		self.getScript().onTimer( self, id, userArg )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		INFO_MSG( self.className, self.spaceID, params[ "databaseID" ], params[ "playerName" ] )
		self.getScript().onEnter( self, baseMailbox, params )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		INFO_MSG( self.className, self.spaceID, params[ "databaseID" ], params[ "playerName" ] )
		self.getScript().onLeave( self, baseMailbox, params )

	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		�˽ӿ�����֪ͨ��ɫ���ص�ͼ��ϣ������ƶ��ˣ�����������������Ϸ���ݽ�����
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		"""
		self.getScript().onTeleportReady( self, baseMailbox )

	def timeFromCreated( self ) :
		"""
		��ȡ�Ӵ��������ô˷�����ʱ��
		"""
		return time.time() - self.createdTime


#
# $Log: not supported by cvs2svn $
# Revision 1.48  2008/07/23 03:13:55  kebiao
# add:spaceType
#
# Revision 1.47  2007/12/26 09:03:38  phw
# method modified: __init__(), ȥ����self.getScript().initEntity( self ),ԭ���ǵײ� GameObject ���Ѿ�����
#
# Revision 1.46  2007/10/03 07:39:27  phw
# ��������
# method removed:
#     _createTransport(), �Ƶ�ObjectScripts/Space.py
#     _createDoor(), �Ƶ�ObjectScripts/Space.py
#     registerPlayer(), ֻ��SpaceCopy���д��ڴ˷����ı�Ҫ
#     unregisterPlayer(), ֻ��SpaceCopy���д��ڴ˷����ı�Ҫ
#
# Revision 1.45  2007/09/29 05:56:12  phw
# �޸���registerPlayer(), unregisterPlayer()������ʵ�ַ�ʽ��
# �޸�onEnter(), onLeave()�����Ĳ���cellMailboxΪbaseMailbox
#
# Revision 1.44  2007/09/24 08:30:30  kebiao
# add:onTimer
#
# Revision 1.43  2007/09/22 09:04:08  kebiao
# ���µ��������
#
#
#