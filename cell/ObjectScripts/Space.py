# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.10 2008-07-23 03:14:04 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import csconst
from bwdebug import *
from GameObject import GameObject
from Resource.PatrolMgr import PatrolMgr
g_patrolMgr = PatrolMgr.instance()

class Space( GameObject ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		GameObject.__init__( self )
		self._spaceConfigInfo = {}
		self._spaceType = csdefine.SPACE_TYPE_NORMAL

		# �Ƿ��ɸ���ȥ����pkֵ�� Ĭ���������role->die�ӿڼ��㡣
		# ���ڸ����кܶ಻ͬ������ ���ָ�����pk������pkֵ�� ��Щ����ֻ���ض��Ķ��ּ���pkֵ�� ���
		# ���������󸱱����Խ��ñ������Ϊtrue����������������һ����ǩ"CalcPkValue"�� Ȼ������onRoleDie
		# ʵ�ֲ�ͬ������.
		self.isSpaceCalcPkValue = False
		self.isDiffCampTeam = False							# �Ƿ�����ͬ��Ӫ��������
		self.canPk = False									# �Ƿ�����pk
		self.canQieCuo = False								# �Ƿ������д�
		self.isSpaceDesideDrop = False
		self.canArrest = False								# �˵�ͼ�Ƿ���Դ����ﷸ
		self.canFly = False									# �˵�ͼ�Ƿ���Է���
		self.canVehicle = True								# �˵�ͼ�Ƿ�����ٻ����
		self.canConjureEidolon = True						# �˵�ͼ�Ƿ�����ٻ�С����
		self.deathDepth = 0									# �ڴ˵�ͼ����������ʱ��������
		self.canGetAccum = 0								# �˵�ͼɱ���Ƿ���Ի������ֵ
		self.canConjurePet = True							# �˵�ͼ�Ƿ�����ٻ�����
		self.playerAoI = None								# �����Ұ��Χ(AoI)�뾶�������None���򲻶�AoI��������
		self.campHonourReward = False

		# �˵�ͼ�Ŀռ���Ӻ�����
		self.minBBox = ( 0, 0, 0 )
		self.maxBBox = ( 0, 0, 0 )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		GameObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "dirmapping", section["dirMapping"].asString )	# chunk ·��
		g_patrolMgr.loadUserString( section["dirMapping"].asString )
		self.setEntityProperty( "timeon", section["TimeOn"].asInt )
		if section.has_key( "SpaceType" ):
			self._spaceType = eval( "csdefine." + section["SpaceType"].asString )
		if section.has_key( "TimeOfDay" ):
			self._timeOfDay = section["TimeOfDay"].asInt
		if section.has_key( "DiffCampTeam" ):
			self.isDiffCampTeam = True
		if section.has_key( "CalcPkValue" ):
			self.isSpaceCalcPkValue = True
		if section.has_key( "CanPk" ):
			self.canPk = section["CanPk"].asInt
		if section.has_key( "SpaceDesideDrop" ):
			self.isSpaceDesideDrop = True
		if section.has_key( "canArrest" ):
			self.canArrest = True
		if section.has_key( "canFly" ):
			self.canFly = bool( section["canFly"].asInt )
		if section.has_key( "CanQieCuo" ):
			self.canQieCuo = section["CanQieCuo"].asInt
		if section.has_key( "canVehicle" ):
			self.canVehicle = bool( section["canVehicle"].asInt )
		if section.has_key( "canConjureEidolon" ):
			self.canConjureEidolon = section["canConjureEidolon"].asInt
		if section.has_key( "canGetAccum" ):
			self.canGetAccum = section["canGetAccum"].asInt
		if section.has_key( "canConjurePet" ):
			self.canConjurePet = section["canConjurePet"].asInt
		if section.has_key( "playerAoI" ) :
			self.playerAoI = section["playerAoI"].asFloat
		if section.has_key( "campHonourReward" ):
			self.campHonourReward = True

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		GameObject.load( self, section )

		spaceSec = section["Space"]

		# ��ȡTransport��Ϣ
		if spaceSec.has_key("Transport"):
			self._spaceConfigInfo[ "Transport" ] = {}
			dict = self._spaceConfigInfo[ "Transport" ]
			for objName, sect in spaceSec._Transport.items():
				dict = {"name" : sect.readString("Name")}
				dict["position"] = sect.readVector3("Pos")
				dict["radius"] = sect.readFloat("radius")
				dict["transportSign"] = sect.readInt64("Sign")
				dict["uid"] = 0

		#��ȡDoor
		doormap = {}
		keys = spaceSec.keys()
		self._spaceConfigInfo[ "Doormap" ] = doormap

		try:
			KeySect = spaceSec.child(keys.index("Door"))
			for name, sect in KeySect.items():
				doordict = {"name" : sect.readString("Name")}
				doordict["position"] = sect.readVector3("Pos")
				doordict["radius"] = sect.readFloat("radius")
				doordict["destSpace"] = sect.readString("DestSpace")
				doordict["destPosition"] = sect.readVector3("DestPos")
				doordict["destDirection"] = sect.readVector3("DestDirection")
				doordict["modelNumber"] = sect.readString("modelNumber")
				doordict["modelScale"] = sect.readFloat("modelScale")
				doormap[name] = doordict
		except:
			pass

		# ����ռ�������Ӻ����ã����ʼ�� by mushuang
		if spaceSec.has_key( "spaceBBoxMin" ) and spaceSec.has_key( "spaceBBoxMax" ):
			bboxMinStr = spaceSec[ "spaceBBoxMin" ].asString
			bboxMaxStr = spaceSec[ "spaceBBoxMax" ].asString

			minCoordAry = bboxMinStr.split( "," )
			maxCoordAry = bboxMaxStr.split( "," )
			assert len( minCoordAry ) == 3, "spaceBBoxMin is not in correct format( x,y,z required )"
			assert len( maxCoordAry ) == 3, "spaceBBoxMax is not in correct format( x,y,z required )"

			try:
				minBBox = ( float( minCoordAry[0] ), float( minCoordAry[1] ), float( minCoordAry[2] ) )
				maxBBox = ( float( maxCoordAry[0] ), float( maxCoordAry[1] ), float( maxCoordAry[2] ) )
			except:
				assert False, " Incorrect format of spaceBBoxMin/spaceBBoxMax, number needed! "

			assert minBBox[ 0 ] < maxBBox[ 0 ] and minBBox[ 1 ] <= maxBBox[ 1 ] and minBBox[ 2 ] < maxBBox[ 2 ], "Coordinate of spaceBBoxMin should be smaller than spaceBBoxMax's"

			self.minBBox = minBBox
			self.maxBBox = maxBBox

		# ��ȡ�����������
		self.deathDepth = spaceSec.readFloat( "deathDepth", -100.0 )

	def getSpaceType( self ):
		return self._spaceType

	def getSpaceConfig( self ):
		"""
		"""
		return self._spaceConfigInfo

	def getTimeOfDay( self ):
		return self._timeOfDay

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		self._createDoor( selfEntity )
		self._createTransport( selfEntity )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		if self.campHonourReward and killer:
			role.camp_beKilled( killer )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		pass

	def onSpaceDestroy( self, selfEntity ):
		"""
		��space entity��onDestroy()����������ʱ�����˽ӿڣ�
		�ڴ����ǿ��Դ���һЩ���飬��Ѽ�¼���������ȫ�����͵�ָ��λ�õȣ�
		"""
		pass

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		"""
		#�������  packedDomainDataInTo ��д�ű�ʱ��Ӧ�ö�Ӧ���������
		�������10��
		params = self.packedDataInTo( player )
		if params[ "level" ] < 10:
			return csstatus.SPACE_MISS_LEVELLACK
		��ĳ����
		if not entity.getTeamMailbox():
			return csstatus.SPACE_MISS_NOTTEAM
		�����ж�
		if not entity.corpsID:
			return csstatus.SPACE_MISS_NOTCORPS
		��Ʒ�ж�
		for name, bag in entity.kitbags.items():
			if bag.find2All( self.__itemName ):
				if self.val == self.__itemName:
					return csstatus.SPACE_OK
		return csstatus.SPACE_MISS_NOTITEM
		"""
		return csstatus.SPACE_OK

	def checkDomainLeaveEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ��뿪������
		���ӣ�ĳ���������û�ﵽĳĿ��ʱ�� ��Զ�������뿪�� �������.
		"""
		return csstatus.SPACE_OK

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		gotoPlane = entity.queryTemp( "gotoPlane", False )
		if gotoPlane:
			return { "gotoPlane":gotoPlane }
		return {}

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = {}
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		pickDict = {}
		pickDict[ "databaseID" ] = entity.databaseID
		pickDict[ "playerName" ] = entity.playerName
		return pickDict

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		if self.playerAoI is not None:
			INFO_MSG("Set entity(ID:%i) AoI to %.1f on enter space %s." % ( baseMailbox.id, self.playerAoI, self.className ))
			BigWorld.entities[baseMailbox.id].setAoIRadius( self.playerAoI )			# ����ռ�������ҵ�AoI

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		if self.playerAoI is not None:
			INFO_MSG("Recover entity(ID:%i) AoI to %.1f on leave space %s." % ( baseMailbox.id, csconst.ROLE_AOI_RADIUS, self.className ))
			player = BigWorld.entities.get( baseMailbox.id )
			if hasattr(player, "setAoIRadius"):							# ���Ա���������ͻ���ʹ��BigWorld.disconnect�����Ͽ����ӣ�������ʱplayer��û��setAoIRadius����
				player.setAoIRadius( csconst.ROLE_AOI_RADIUS )			# �뿪�ռ���ָ�Ĭ�ϵ�AoI

	def _createTransport( self, selfEntity ):
		"""
		����Transport
		"""
		print "Create createTransport..."
		configInfo = self.getSpaceConfig()
		if configInfo.has_key("Transport"):
			for projDict in configInfo[ "Transport" ]:
				BigWorld.createEntity("SpaceTransport", selfEntity.spaceID, projDict["position"], (0, 0, 0), projDict )

	def _createDoor( self, selfEntity ):
		"""
		����Door
		"""
		print "Create createDoor..."
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "Doormap" ].iteritems():
			print "create Door ", name
			BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 0), otherDict )


	def onLeaveTeam( self, playerEntity ):
		"""
		��Ա�뿪����֪ͨ����space��script
		"""
		pass

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		��Ա�뿪���鴦��
		"""
		pass

	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		������ϣ�����Ѿ�����ռ�
		"""

		if self.canFly:
			# ����ռ���Է��У��Ϳ����ͷ�����صĸ��ּ�⣬����ر���ؼ��
			baseMailbox.client.enableFlyingRelatedDetection( self.minBBox, self.maxBBox )
		else:
			baseMailbox.client.disableFlyingRelatedDetection()


	def canUseSkill( self, playerEntity, skillID ):
		"""
		�Ƿ��ܹ�ʹ�ÿռ�ר������
		"""
		return False

	def requestInitSpaceSkill( self, playerEntity ):
		# �����ʼ����������
		pass

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		pass

	def copyTemplate_onMonsterDie( self, spaceBase, monsterID, monsterClassName, killerID ):
		"""
		�¸���ģ��Ĺ�������֪ͨ
		"""
		pass

	def onEntitySpaceGone( self, entity ):
		"""
		called when the space this entity is in wants to shut down. 
		"""
		pass

# $Log: not supported by cvs2svn $
# Revision 1.9  2008/03/07 06:39:14  kebiao
# ���Ѳ����ع���
#
# Revision 1.8  2008/02/04 07:44:39  phw
# �޸�����������
#
# Revision 1.7  2007/12/15 11:27:37  huangyongwei
# onLoadEntityProperty ��Ϊ onLoadEntityProperties
#
# Revision 1.6  2007/10/03 07:40:42  phw
# ��������
# method added:
#     _createTransport(), ����SpaceNormal.py
#     _createDoor(), ����SpaceNormal.py
#
# Revision 1.5  2007/09/29 06:55:37  phw
# method modified: onLoadEntityProperties_(), ����"TimeOn"������ȡ����ȷ��bug
#
# Revision 1.4  2007/09/29 06:52:01  phw
# method modified: onLoadEntityProperties_(), dirMapping -> dirmapping, TimeOn -> timeon��������space�Ҳ�����ͼ���ݵ�����
#
# Revision 1.3  2007/09/29 05:59:34  phw
# �޸��ˡ�dirMapping������TimeOn���Ķ�ȡλ�ã���ԭ����Load()ת�Ƶ�onLoadEntityProperties_()
# ������onSpaceDestroy()�ص���
# �޸�onEnter(), onLeave()�Ĳ���cellMailboxΪbaseMailbox
#
# Revision 1.2  2007/09/24 08:30:17  kebiao
# add:onTimer
#
# Revision 1.1  2007/09/22 09:09:19  kebiao
# space�ű�������
#
#
#
