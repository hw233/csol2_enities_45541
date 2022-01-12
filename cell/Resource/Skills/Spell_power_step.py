# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from Spell_PhysSkill import Spell_PhysSkill
import Love3

class Spell_power_step( Spell_PhysSkill ):
    """
    怪力践踏
    """
    def init( self, dictData ):
        """。
        """

        self._range = float( dictData[ "param1" ] if len( dictData[ "param1" ] ) > 0 else 0 )
        Spell_PhysSkill.init( self, dictData )



    def receive( self, caster, receiver ):
        """
        virtual method.
        技能实现的目的
        """
        if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ): 
     	   receiver.client.shakeCamera( 0.5, caster.position - receiver.position )
        Spell_PhysSkill.receive( self, caster, receiver )

