# -*- coding: gb18030 -*-

# BigWorld
import BigWorld
# client
import event.EventCenter as ECenter

class RoleStarMapInterface:
	"""
	�Ǽʵ�ͼ���
	"""
	def __init__( self ):
		self.pgNagualSkills = {}
		
	def showPGControlPanel( self, skills ):
		"""
		define method
		�����̹��ػ��ٻ��Ϳ��ƽ���
		"""
		ECenter.fireEvent( "EVT_ON_TRIGGER_PG_CONTROL_PANEL", skills )

	def closePGControlPanel( self ):
		"""
		define method
		�ر��̹��ػ��ٻ��Ϳ��ƽ���HP
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_PG_CONTROL_PANEL" )
		
	def onClientGetPGSkill( self, skillID, realm ):
		"""
		�����������̹��ػ�ĳ�����ܵ�����
		"""
		if realm == 0 and self.livingskill.has_key( skillID ):
			self.pgNagualSkills.pop( skillID )
			return
		self.pgNagualSkills[skillID] = realm

		#self.onUpdateSkill_2( skillID, skillID )
		
	def onUpdateSkill_2( self, oldSkillID, newSkillID ):
		"""
		����һ������ ������ʾ��Ϣ�汾
		@type		oldSkillID : INT
		@param		oldSkillID : �ɵļ��� ID
		@type		newSkillID : INT
		@param		newSkillID : �µļ��� ID
		@return				   : None
		"""
		for index, skillID in enumerate( self.skillList_ ) :
			if skillID == oldSkillID :
				self.skillList_[index] = newSkillID
				break
		sk = skills.getSkill( newSkillID )
		itemInfo = SkillItemInfo( sk )
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_UPDATE_SKILL", oldSkillID, itemInfo )
		
	def set_accumPoint( self, oldValue ):
		"""
		���˵���
		"""
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_ACCUMPOINT_CHANGE", self.accumPoint )
	
	def addMapSkill( self, index, skillID ):
		"""
		����ٻ��ػ�����
		"""
		self.cell.addMapSkill( index, skillID )
	
	def removeMapSkill( self, index ):
		"""
		�Ƴ��ٻ��ػ�����
		"""
		self.cell.removeMapSkill( index )
	
	def onAddMapSkill( self, index, skillID ):
		"""
		�����ػ����ܻص�
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_ADD_MAPSKILL", index, skillID )
	
	def onRemoveMapSkill( self, index ):
		"""
		�Ƴ��ػ����ܻص�
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_REMOVE_MAPSKILL", index )
	