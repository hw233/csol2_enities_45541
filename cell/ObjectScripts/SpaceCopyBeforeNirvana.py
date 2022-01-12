# -*- coding: gb18030 -*-

# 10 �����鸱�� 
# alienbrain://PROJECTSERVER/����Online/��ɫ�汾/09_��Ϸ����/05_�������/04_���鸱��/10�����鸱��.docx
# programmed by mushuang 

from SpaceCopy import SpaceCopy
import BigWorld
import csdefine

SPACE_SKILL_BUFF_ID = 22019
# ���Ƶ���Ϊ
STATE = csdefine.ACTION_FORBID_CHANGE_MODEL | csdefine.ACTION_FORBID_VEHICLE

class SpaceCopyBeforeNirvana( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spaceSkills = { csdefine.CLASS_FIGHTER:[], \
							csdefine.CLASS_SWORDMAN:[], \
							csdefine.CLASS_ARCHER:[], \
							csdefine.CLASS_MAGE:[], \
							}
		
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ��ȡ���븱��Ҫչ���Ļ���ID
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerClass" ] = entity.getClass()
		scrollID = entity.popTemp( "ScrollIDOnEnter" )
		if scrollID is not None:
			packDict["ScrollIDOnEnter"] = scrollID
		return packDict
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		self.spaceSkills[csdefine.CLASS_FIGHTER] = [ int( skillID ) for skillID in section.readString( "fighterSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_SWORDMAN] = [ int( skillID ) for skillID in section.readString( "swordmanSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_ARCHER] = [ int( skillID ) for skillID in section.readString( "archerSkills" ).split( ";" ) ]
		self.spaceSkills[csdefine.CLASS_MAGE] = [ int( skillID ) for skillID in section.readString( "mageSkills" ).split( ";" ) ]
		
	def canUseSkill( self, playerEntity, skillID ):
		"""
		�ж��Ƿ��������ʹ�ó����ض�����
		"""
		return skillID in self.spaceSkills[playerEntity.getClass()]
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		baseMailbox.cell.actCounterInc( STATE )
		baseMailbox.client.initSpaceSkills( self.spaceSkills[params["playerClass"]], csdefine.SPACE_TYPE_BEFORE_NIRVANA )
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		baseMailbox.cell.actCounterDec( STATE )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def requestInitSpaceSkill( self, playerEntity ):
		# ��ʼ����������
		playerEntity.client.initSpaceSkills( self.spaceSkills[ playerEntity.getClass() ], csdefine.SPACE_TYPE_BEFORE_NIRVANA )

