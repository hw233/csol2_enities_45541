# -*- coding: gb18030 -*-
#


"""
"""
import BigWorld
import csstatus
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine
#��Ӧ�Ա��Ӧְҵ�Ķ��踱��NPC��className
classNames = {csdefine.GENDER_MALE:{csdefine.CLASS_FIGHTER:"10121772",  \
									csdefine.CLASS_SWORDMAN:"10121774", \
									csdefine.CLASS_ARCHER:"10121776",   \
									csdefine.CLASS_MAGE:"10121778"      \
				},\
			  csdefine.GENDER_FEMALE:{csdefine.CLASS_FIGHTER:"10121773", \
			  						  csdefine.CLASS_SWORDMAN:"10121775",\
			  						  csdefine.CLASS_ARCHER:"10121777",  \
			  						  csdefine.CLASS_MAGE:"10121779"     \
			  }}
class SpaceCopyDance( SpaceCopy ):
	def __init__(self):
		SpaceCopy.__init__(self)
		self.spaceSkills = []
		
		
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'dbID' : entity.databaseID ,"class":entity.getClass() ,"gender":entity.getGender(),"spaceKey":entity.databaseID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		pickDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		pickDict["class"] = entity.getClass()
		pickDict["gender"] = entity.getGender()
		return pickDict		
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		# �������ķ�ʽ���븱��
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		entity = g_objFactory.getObject( classNames[params["gender"]][params["class"]] ).createEntity( selfEntity.spaceID, (42.7,0,54.7), (0,0,0), {} )
		DEBUG_MSG("create entity DanceNPC %d"%entity.id)
		
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		self.spaceSkills = [ int( skillID ) for skillID in section.readString( "spaceSkills" ).split( ";" ) ]
		
	def canUseSkill( self, playerEntity, skillID ):
		"""
		�ж��Ƿ��������ʹ�ó����ض�����
		"""
		return skillID in self.spaceSkills	
	