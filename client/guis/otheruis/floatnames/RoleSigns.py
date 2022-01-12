# -*- coding: gb18030 -*-
#
# role special sign & show formula
# written by gjx 2009-4-3
#

from bwdebug import *
from guis.common.PyGUI import PyGUI
import BigWorld
class RoleSigns( PyGUI ) :

	# ����ǰ������ȼ���ߣ����һ�����ȼ����
	_SIGN_MAPS = [
				( "cityWarer", "maps/entity_signs/fungus.texanim" ),	# ��ս�ɵ�Ģ����
				( "bloodyItem", "maps/npc_signs/tb_npc_jie_001.tga" ),	# ��Ѫ��Ʒ���
				( "merchant", "maps/npc_signs/tb_npc_shang_002.tga" ),	# ���̱��
				( "pillage", "maps/npc_signs/tb_npc_fei_001.tga" ),		# ����������
				( "captain", "maps/npc_signs/tb_js_qi_zi_001.tga" ),	# �ӳ����
				( "teammate", "maps/npc_signs/tb_js_qi_zi_002.tga" ),	# �Ƕӳ���Ա���
				]

	def __init__( self, guiObject ) :
		PyGUI.__init__( self, guiObject )

		# ��ʾ��ǣ�����ָ����ǰ��Щ�����Ҫ��ʾ�ģ����������ȼ�������ʾ��
		self.__signFlags = {}
		self.__initFlags()
		self.__tongSign = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initFlags( self ) :
		"""
		������ͼ����Ӧ�ı�ǣ�ָ����ǰ�Ƿ���ʾ�ñ��
		"""
		for flagName, texture in self._SIGN_MAPS :
			self.__signFlags[flagName] = False							# ��ʼ�����б�ǣ�Ĭ�ϲ���ʾ

	def __updateSign( self ) :
		"""
		������Ҫ��ʾ�ı��
		"""
		for flagName, texture in self._SIGN_MAPS :
			if self.__signFlags[flagName] :								# ��ʾ���ȼ���ߵı��
				self.texture = texture
				self.visible = True
				if self.texture == "" :
					ERROR_MSG( "Can't find texture:", self._SIGN_MAPS[flagName] )
				break
		else :
			self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showSign( self, entityID, sign, isShow ) :
		"""
		ָ����ʾ/����ĳ�����
		"""
		player = BigWorld.player()
		if self.__signFlags.has_key( sign ) :
			if sign == "captain"and isShow and not player.isTeamMember( entityID ) and player.isInTeam():
					self.__signFlags[sign] = False	# �����Ҽ�����һ�����飬����ʾ��������Ķӳ���־
			elif sign == "teammate"and isShow and not player.isTeamMember( entityID ):#����ʾ��������Ķ�Ա�����־
					self.__signFlags[sign] = False
			else:
				self.__signFlags[sign] = isShow
			
			self.__updateSign()
		else :
			print "------------->>> unknow role sign:", sign
			
	def hideAllSign( self ):
		"""
		�������еı�ʶ
		"""
		for signName in self.__signFlags.iterkeys():
			self.__signFlags[signName] = False
		self.__updateSign()
