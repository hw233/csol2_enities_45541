# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCopyTeam.py,v 1.2 2008-01-28 06:02:10 kebiao Exp $

"""
�������˽������������ӽ��ĸ�����������wow����ͨ������

a1, a2 ��ʾ��������A�е���������ʵ����
p1, p2, p3��ʾ������������ң�

���븱��ʱ������ж���ID������ĸ�����ֱ�ӽ��룻
p1, p2, p3δ��ӣ�
	��p1����a1, p2����a2����ʱp1��p2��ӣ��ӳ�Ϊp1����ʱ
		������������ɢ��ʲô����Ҳû����
		��p2�뿪a2���ؽ�A�����ڶ���û�и�����¼����ʱӦ�ý���a1�����Զӳ��ĸ���Ϊ���鸱�����������ö��鸱����¼
		��p1�뿪a1���ؽ�A�����ڶ���û�и�����¼����ʱӦ�ý���a1�����Զӳ��ĸ���Ϊ���鸱�����������ö��鸱����¼
			����������������������p3������飬���븱��Aʱ������p3�Ƿ�Ϊ�ӳ�����Ӧ�ý�������¼�ĸ�������a1��
		��p3������飬�Ƕӳ�������A�����ڶ���û�и�����¼����ʱӦ�ý������紴���ĸ���ʵ���������ö��鸱����¼
		��p3������飬���Ƕӳ�������A�����ڶ���û�и�����¼����ʱӦ�ý���a1�����Զӳ��ĸ���Ϊ���鸱�����������ö��鸱����¼
			������������������󣬴�ʱ
				�������ɢ��p1,p2������ɶ��飬����A��p1ԭ���Ƕӳ����и�����¼��������p1�и��������˸����ǹ�����һ������ģ����Ӧ���½����������ö��鸱����¼�����ø���������Ϊ�ӳ�
				���ӳ���p1��Ϊp2��p1�뿪���飬���뿪��ǰ�������ؽ�A������ԭ�����ǹ�������ģ����ԣ������ؽ��¸��������ô�����Ϊp1
					���ʣ�ԭ������a1�Ĵ�����˭����������ɢ���Ժ�ø�������˭��
					����ԭ����a1�����߶�ʧ�������ʱ�����ɢ����ȥ�󽫲��������һش˸�����
					���ʣ�����ڸ����н�ɢ������ٴ������齨���飬�˸����Ƿ���Ч��
					��������ÿ������id�ڶ�ʱ���ڶ���Ψһ�ģ���ʹ�ڸ����ڽ�ɢ��������飬Ҳ�޷���ȡԭ���ĸ�����������뿪�������ؽ�ʱ����Ȼ���½�������û�ж����¼�ĸ������ҵ�ǰ�ӳ����ڵĸ�����������һ�����飬ֻ���½�����
				���ӳ���ѡ�ı䣬��������ɢ���Ժ�ø�������˭��
					��������һ��������ô�������޷����һأ�����һ��ʱ����Զ���ʧ��

p1,p2��û�н���A��p1,p2��ӣ�����A����ʱ
	�����ڶ���û�и�����¼�������˶�û�и�����¼����˴����¸����������ö���Ϊ������¼�����ø���������Ϊ�ӳ�

�ۺ����Ϲ��򣬸�����ͼ�����ж��Ⱥ�˳�����£�
p1���븱����ͼ
	p1�����
		���ݶ���ID���ҵ�����Ӧ��spaceʵ��a1��ֱ�ӽ���a1��over��
		���ݶ���ID��û�ҵ���Ӧ��spaceʵ��
			���ݶӳ�dbid���ҵ�����Ӧ��spaceʵ��a1����a1û�������ID�������ʹa1�����ID�����������a1��over��
			���ݶӳ�dbid���Ҳ�����ص�spaceʵ�������ҵ������Ѿ������ID�������
				����ʣ���Ա��dbid����û�������ID�������spaceʵ����
					�ҵ��ˣ�ȡ���紴����spaceʵ��a1��ʹa1�����ID�����������a1��over��
					�Ҳ�����������һ��
				��һ��Ϊ��(û���ҵ�)�������¸���a1��ʹa1�Ĵ�����Ϊ�ӳ�DBID��ʹa1�����ID�����������a1��over��
	p1δ��ӣ����Լ���dbid������ص�spaceʵ��
		�ҵ���ֱ�ӽ��룬over��
		�Ҳ����������¸���a1��ʹa1�Ĵ�����Ϊ�Լ���dbid������a1��over��
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopy import SpaceDomainCopy
import csdefine

# ������
class SpaceDomainCopyTeam(SpaceDomainCopy):
	"""
	�������˽������������ӽ��ĸ�����������wow����ͨ������
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__(self)

		# ����������������ӳ�����entityID��spaceNumber֮��Ĺ�ϵ��
		# ���ڵ���ҽ���ĳ��spaceʱ��ȷ�����Ѵ��ڵ�space�Ƿ��ж������Ȩ��
		# �����������д��ڵ�ֵ��������ϵ����ĳ�����Դ���ĳ��key/valueʱ����һ��Ҳ����һ����֮��Ӧ��value/key
		self.__spaceNumber2teamID = {}		# key = space number,	value = team entity id
#		self.teamID2spaceNumber = {}		# key = team entity id,	value = space number
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS

	def createSpaceItem( self, param ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		# ���ڵ�ǰ�Ĺ����Ǵ����߲��ᣨҲ�����ܣ����Ŷӳ��ĸı���ı䣬
		# �����ǰ�����Ĵ������뿪�˶��飬Ȼ���Լ����ⴴ������ʱ��
		# �µĸ����ͻḲ�Ǿɵĸ��������ھɵĸ�������Ĵ����߻������ڵ���ң�
		# ���ɵĸ����ȸ�����´����ĸ����ȹر�ʱ����Ȼ�ᵼ���µĸ���ӳ�䱻ɾ����
		# ��ˣ�Ϊ�˱�������bug���ڴ����µĸ���ʱ�����Ǳ����Ȳ��ҵ�ǰ����Ƿ��Ѵ����˸�����
		# ���������Ҫ�ȰѾɸ����Ĵ�������0����û�д����߻򴴽��߶�ʧ�����ſ��Դ����µĸ�����
		spaceItem = self.getSpaceItemByDBID( param.get( "dbID" ) )
		if spaceItem:
			spaceItem.params["dbID"] = 0

		spaceItem = SpaceDomainCopy.createSpaceItem( self, param )
		if spaceItem and param.get( "teamID" ):	# �������µ�spaceItem��������ˣ�û���ֵӦ����0��None���������øø���Ϊ���鸱��
			self.setTeamRelation( param.get( "teamID" ), spaceItem.spaceNumber )
		return spaceItem

	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		ģ�巽����ɾ��spaceItem
		"""
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )
		self.removeTeamRelation( spaceNumber )

	def setTeamRelation( self, teamEntityID, spaceNumber ):
		"""
		����ĳ��space�����Ĺ�ϵ
		"""
		self.keyToSpaceNumber[teamEntityID] = spaceNumber
		self.__spaceNumber2teamID[spaceNumber] = teamEntityID
		SpaceDomainCopy.setTeamRelation( self, teamEntityID, spaceNumber )

	def removeTeamRelation( self, spaceNumber ):
		"""
		�Ƴ�ĳ��space�����Ĺ�ϵ
		@param value: INT, spaceNumber
		"""
		if spaceNumber in self.__spaceNumber2teamID:
			v = self.__spaceNumber2teamID.pop( spaceNumber )
			self.keyToSpaceNumber.pop( v )
			SpaceDomainCopy.removeTeamRelation( self, v )

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		�ռ�رգ�space entity����֪ͨ��
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		self.notifyTeamSpaceClosed( spaceNumber )		# ֪ͨ�󶨵Ķ��鸱���ر���
		self.removeTeamRelation( spaceNumber )	# ���Ƴ�������spaceItem�Ĺ�ϵ
		SpaceDomainCopy.onSpaceCloseNotify( self, spaceNumber )

	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
		"""
		spaceItem = self.findSpaceItem( params, False )
		dbid = params[ "dbID" ]
		if spaceItem:
			if not self.isKickNotOnlineMember( spaceItem.spaceNumber, dbid ):
				spaceItem.logon( baseMailbox )
				self.clearKickNotOnlineMember( dbid )
				return
		
		self.clearKickNotOnlineMember( dbid )	
		baseMailbox.logonSpaceInSpaceCopy()

	def getSpaceNumberByTeamID( self, teamID ):
		"""
		"""
		if not self.keyToSpaceNumber.has_key( teamID ):
			return 0
		return self.keyToSpaceNumber[teamID]

	def queryBossesKilledByTeamID( self, querist, teamID ) :
		"""
		<Define method>
		@type	querist : MAILBOX
		@param	querist : ��ѯ�ߣ�������ж��巽��onQueryBossesKilledCallback
		@type	teamID : OBJECT_ID
		@param	teamID : ����ID
		"""
		spaceItem = self.getSpaceItem( self.getSpaceNumberByTeamID( teamID ) )
		if spaceItem is None :
			ERROR_MSG( "Can't find map space copy by teamID %i." % teamID )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# �ص�һ����������ʾ������
		elif spaceItem.baseMailbox is None :
			ERROR_MSG( "SpaceCopy(%s) of team(ID:%i) base mailbox is None ." %\
				( self.__class__.__name__, teamID, ) )
			querist.onQueryBossesKilledCallback( teamID, -1 )						# �ص�һ����������ʾ������
		else :
			spaceItem.baseMailbox.queryBossesKilled( querist, teamID )

	def notifyTeamSpaceClosed( self, spaceNumber ) :
		"""
		֪ͨ�͸����󶨵Ķ��飬�����ر���
		"""
		if spaceNumber in self.__spaceNumber2teamID :
			teamID = self.__spaceNumber2teamID[spaceNumber]
			BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "onMatchedCopyClosed", () )
		else :
			# �ߵ��ⲽ���ܵ�ԭ��֮һ�ǣ���֮ǰƥ��ĸ����ر�֮ǰ������������ƥ�䵽���µĸ���
			WARNING_MSG("Can't find map team to space(spaceNumber:%i)." % spaceNumber)

	def notifyTeamRaidFinished( self, spaceNumber ) :
		"""
		<Define method>
		֪ͨ�͸����󶨵Ķ��飬����Raid�Ѿ����
		@type		spaceNumber : SPACE_NUMBER
		@param		spaceNumber : ����ʵ����Ψһ���
		"""
		if spaceNumber in self.__spaceNumber2teamID :
			teamID = self.__spaceNumber2teamID[spaceNumber]
			BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "onMatchedRaidFinished", () )
		else :
			# �ߵ��ⲽ���ܵ�ԭ��֮һ�ǣ���֮ǰƥ��ĸ����ر�֮ǰ������������ƥ�䵽���µĸ���
			WARNING_MSG("Can't find map team to space(spaceNumber:%i)." % spaceNumber)


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/10/07 07:13:39  phw
# no message
#
#