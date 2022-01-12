# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.6 2008-04-23 04:01:12 kebiao Exp $

"""
����NPC����
"""

from NPCObject import NPCObject
from bwdebug import *
from NPCBaseAttrLoader import NPCBaseAttrLoader					# ��������������Լ�����
from MonsterIntensifyPropertyData import MonsterIntensifyPropertyData
from NPCExpLoader import NPCExpLoader								# ���ﾭ�������
import ItemTypeEnum
import csdefine
import csconst
import random
g_npcBaseAttr = NPCBaseAttrLoader.instance()
g_npcExp = NPCExpLoader.instance()
g_monsterIntensifyAttr = MonsterIntensifyPropertyData.instance()

class Monster(NPCObject):
	"""
	����NPC��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		self.equips = {}						# �����װ���б�key == order, value == itemID
		self.aiData	= {}						# �����AI���ݱ�
		self._expRate = 0.0						# ���ﾭ����ʵļ���
		self.callList = []						# ����ͬ��� [npcid,...]
		self.attrAIDefLevel = 0					# �����Ĭ��AI�ȼ�
		self.prestige = []						# ��ɱ�������ǿɻ�õ�����ֵ��[ (id, value), ...]; id == ����������value == ���ӵ�����

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPCObject.onLoadEntityProperties_( self, section )

		# �Ա�ְҵ�����塢����
		raceclass = 0
		#raceclass += section.readInt( "gender" )			# ��ʱ���Դ˹��ܣ�ȫ��Ĭ��Ϊ�У���Ϊ�߻��ⲿ����ʱû����
		raceclass |= section.readInt( "class" ) << 4
		raceclass |= section.readInt( "race" ) << 8
		raceclass |= section.readInt( "faction" ) << 12
		self.setEntityProperty( "raceclass", raceclass )
		self.setEntityProperty( "level", section.readInt( "level" ) )
		self._expRate = section.readFloat( "expRate" )
		self.setEntityProperty( "baseAtt", section.readFloat( "baseAtt" ) )

		# AI
		self.setEntityProperty( "petModelScale",			section.readFloat( "petModelScale" ) )			# ����׽Ϊ������ģ�����ű��� 2008-12-5 add by gjx
		#self.setEntityProperty( "attackSkill",				section.readInt("attackSkill") )				# �������ܣ��޴˼���ʱΪ������
		if section.has_key( "walkPath" ):
			self.setEntityProperty( "walkPath",				eval(section.readString("walkPath")) )			# Ѳ��·��
		if section.has_key( "initiativeRange" ):
			self.setEntityProperty( "initiativeRange",		section["initiativeRange"].asFloat )			# ����������Χ
		self.setEntityProperty( "range_base",				int( section["range_base"].asFloat * csconst.FLOAT_ZIP_PERCENT ) )					# �����������ֵ
		self.setEntityProperty( "viewRange",				section["viewRange"].asFloat )					# ��Ұ��Χ������������Χ��
		self.setEntityProperty( "territory",				section["territory"].asFloat )					# ����Χ��׷����Χ��
		if section.has_key( "petName" ):
			self.setEntityProperty( "petName",				section["petName"].asString )					# ��������
		if section.has_key( "callRange" ):
			self.setEntityProperty( "callRange",			section["callRange"].asFloat )					# ����ͬ�鷶Χ
		self.attrAIDefLevel = section.readInt("aiLevel")

		# ����ģ����ʾ���
		"""
		modelNumber = section.readString( "lefthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "lefthandNumber", modelNumber )

		modelNumber = section.readString( "righthandNumber" )
		if len( modelNumber ):
			modelNumber = int( modelNumber.replace( "-", "" ), 10 )
		else:
			modelNumber = 0
		self.setEntityProperty( "righthandNumber", modelNumber )
		"""
		self._lefthandNumbers = []
		self._righthandNumbers = []
		if section.has_key( "lefthandNumber" ):
			self._lefthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["lefthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "righthandNumber" ):
			self._righthandNumbers = [ int( e.replace( "-", "" ), 10 ) for e in section["righthandNumber"].readStrings( "item" ) if len( e ) > 0 ]
		if section.has_key( "callList" ):
			for item in section[ "callList" ].values():
				self.callList.append( item.asString )

		# ��¼��С�����ȼ�������ʱ������С�����ȼ��������
		self.minLv = section.readInt("minLv")
		self.maxLv = section.readInt("maxLv")
		
		self.petInbornSkills = []
		petInbornSkills = section.readString( "petInbornSkills" )
		if petInbornSkills != "":
			self.petInbornSkills = [int( skillID ) for skillID in petInbornSkills.split( ";" )]
			
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		NPCObject.load( self, section )
		self.mapPetID = section.readString( "petID" )
		self.takeLevel = section.readInt( "takeLevel" )
		# ������������
		if section["prestige"] is not None:
			for e in section["prestige"].readVector2s( "item" ):
				self.prestige.append( ( int( e[0] ), int( e[1] ) ) )		# ����ת������

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		pass

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		����һ��NPCʵ���ڵ�ͼ��
		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: entity�ĳ���λ��
		@type   position: VECTOR3
		@param direction: entity�ĳ�������
		@type  direction: VECTOR3
		@param      param: �ò���Ĭ��ֵΪNone������ʵ�������
		@type    	param: dict
		@return:          һ���µ�NPC Entity
		@rtype:           Entity
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# ע������Ҫ��g_npcExp���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# ��ְҵ�͵ȼ�Ϊ����������ȫ������
		# ע������Ҫ��g_npcBaseAttr���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		return NPCObject.createEntity( self, spaceID, position, direction, param )

	def createBaseAnywhere( self, param = None, callback = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		@rtype						   : Entity
		@return						   : return a new entity
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# ע������Ҫ��g_npcExp���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# ��ְҵ�͵ȼ�Ϊ����������ȫ������
		# ע������Ҫ��g_npcBaseAttr���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		NPCObject.createBaseAnywhere( self, param, callback )

	def createLocalBase( self, param = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		"""
		if param is None:
			param = {}

		if param.has_key( 'level' ):
			param["level"] = min( param["level"], self.maxLv )
		else:
			param["level"] = random.randint( self.minLv, self.maxLv )
		# ע������Ҫ��g_npcExp���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param["exp"] = g_npcExp.get( param["level"] ) * self._expRate
		if len( self._lefthandNumbers ):
			param["lefthandNumber"] = self._lefthandNumbers[ random.randint( 0, len( self._lefthandNumbers ) - 1 ) ]
		if len( self._righthandNumbers ):
			param["righthandNumber"] = self._righthandNumbers[ random.randint( 0, len( self._righthandNumbers ) - 1 ) ]
		# ��ְҵ�͵ȼ�Ϊ����������ȫ������
		# ע������Ҫ��g_npcBaseAttr���Ե�ǰ��û�Ƶ�common�����cell/ObjectScripts/Monster.py���Ժ���Ҫ�Ƶ�common��
		param.update( g_npcBaseAttr.get( self.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS, param["level"] ) )
		attrs = g_monsterIntensifyAttr.getAttrs( self.className, param["level"] )
		if attrs:
			param.update( attrs )
		return NPCObject.createLocalBase( self, param )

	def getInbornSkills( self ):
		"""
		��ô���monster�����ɳ���ĵ��츳����
		"""
		return self.petInbornSkills
		
# Monster.py
