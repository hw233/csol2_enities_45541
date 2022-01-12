# -*- coding: gb18030 -*-

# BigWorld
import BigWorld
# client
import event.EventCenter as ECenter

class RoleStarMapInterface:
	"""
	星际地图相关
	"""
	def __init__( self ):
		self.pgNagualSkills = {}
		
	def showPGControlPanel( self, skills ):
		"""
		define method
		开启盘古守护召唤和控制界面
		"""
		ECenter.fireEvent( "EVT_ON_TRIGGER_PG_CONTROL_PANEL", skills )

	def closePGControlPanel( self ):
		"""
		define method
		关闭盘古守护召唤和控制界面HP
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_PG_CONTROL_PANEL" )
		
	def onClientGetPGSkill( self, skillID, realm ):
		"""
		服务器返回盘古守护某个技能的数据
		"""
		if realm == 0 and self.livingskill.has_key( skillID ):
			self.pgNagualSkills.pop( skillID )
			return
		self.pgNagualSkills[skillID] = realm

		#self.onUpdateSkill_2( skillID, skillID )
		
	def onUpdateSkill_2( self, oldSkillID, newSkillID ):
		"""
		更新一个技能 不带提示信息版本
		@type		oldSkillID : INT
		@param		oldSkillID : 旧的技能 ID
		@type		newSkillID : INT
		@param		newSkillID : 新的技能 ID
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
		气运点数
		"""
		ECenter.fireEvent( "EVT_ON_PLAYERROLE_ACCUMPOINT_CHANGE", self.accumPoint )
	
	def addMapSkill( self, index, skillID ):
		"""
		添加召唤守护技能
		"""
		self.cell.addMapSkill( index, skillID )
	
	def removeMapSkill( self, index ):
		"""
		移除召唤守护技能
		"""
		self.cell.removeMapSkill( index )
	
	def onAddMapSkill( self, index, skillID ):
		"""
		增加守护技能回调
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_ADD_MAPSKILL", index, skillID )
	
	def onRemoveMapSkill( self, index ):
		"""
		移除守护技能回调
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_REMOVE_MAPSKILL", index )
	