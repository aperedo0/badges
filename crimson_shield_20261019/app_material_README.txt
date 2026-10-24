Crimson Shield runtime brushed field

The owner approved this shield specific app material exception. Production app files have not been changed. Apply app_material.patch to BadgeHeroCard.swift when integrating the shield, reviewing its context against the current renderer first. The patch contains only this material addition, without private picker changes.

The USDZ field material must be named exactly CrimsonShield_BrushedField. On load the app sets its PBR anisotropy to 0.55, angle 0, and supplies straight diagonal tangent vectors matching ShieldUV. Front direction is (0.840, 0.543, 0); back reverses X because it is the front rotated half a turn about Y. Classification uses position Z, then projects onto each actual surface. Bitangent is cross(normal, tangent). The existing floor mirror transforms the prepared basis after cloning.

Only exact matching materials are touched recursively. Coin brushing, gem shader, studio light, geometry, resting angle, placement and glint behavior are unchanged. The edit runs once when loading, with no new shader or render passes.
