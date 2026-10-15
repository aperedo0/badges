# Outline fix: Copper, Bronze, Platinum (2026-10-12/13, Claude)

Owner: "I see a lot [of weird outlines] on copper, bronze, and platinum ... fix them ... also scale up the copper badge a little tiny bit".

Final files in `final/` (models, Badges screen stills, all `usdchecker --arkit` Success). Started from the installed models (repo HEAD b0a800b), kept in `work/<tier>/installed.usdz`.

## What caused the outlines

- **Painted strip:** each badge's front texture was solved from a reference picture, and its outermost few texels kept the reference's rim (earlier "darken only" fixes turned the white rim into a dark or orange stroke).
- **Thin edge parts:** Platinum's edge lip (near black, roughness 0.88) drew a 1 px dark line around every ribbon at rest; its side walls (near black) became thick black bands while turning. Bronze's ray walls and Copper's rolled edge did the same in smaller ways.
- **Bronze ring:** a real see-through gap (0.015 units) between the dome rim and the groove plate, plus a hairline wedge between the two beads, broke the dark groove into black and yellow dashes.
- **Platinum rounded edges:** the edge normals tilt away and mirror a dark (or a bright) part of the studio, so the face ends in a dark or white rim.

## What changed

- **All three:** the outermost 3 screen pixels of each front texture repainted as the smooth (harmonic) continuation of the texels just inside, narrower on thin tips; padding outside the shape refilled by pull push so mipmaps do not bleed a rim. Interior texels untouched. `tools/bandfill.py`.
- **Copper:** 3% larger (scaled about its lowest point: bottom stays at Y -2.455, top 3.004 under the 3.015 limit; 3% is the most it can grow without dropping below the shared float height). Rolled edge strip rougher (0.2, 0.08, 0.035, roughness 0.8).
- **Bronze:** groove plate inner edge moved under the dome (r 1.099 to 1.07) and outer edge behind the outer bead (1.235 to 1.215); inner bead 0.8% larger so it meets the outer bead; groove dark matte (0.06, 0.03, 0.01, roughness 0.6); spike side walls plain bronze (0.29, 0.13, 0.035, roughness 0.5); colors kept warm (G never above R, B never above G) and the dome's yellow-green glow warmed (it showed as an olive patch while turning).
- **Platinum:** edge lip faces join the face they border, with that face's normals and texture coordinates (`tools/lipfix.py`); a 0.07 unit strip along each edge shades like the face just inside it (`tools/edgeflat.py`); side walls plain dark metal (0.22, 0.23, 0.25, roughness 0.6) with normals blended 70% toward the nearest face (`tools/uvfrom.py`).
- Files re-saved with Apple's `usdcat` (Blender's USD writer stored them about twice as big).

## Testing

A private clone of the app and its own simulator (`tools/lab.sh`), so the shared repo and simulator were never touched. Five poses per badge (rest, two turns, back, far): `shots/base5` (before) and `shots/final` (after). Two fresh reviewers compared them at 1x to 4x.

## Known leftovers

- Copper: while turning and from behind, a thin orange dotted rim on some flame edges (the polished edge mirroring light at a grazing angle); present before too, slightly weaker now.
- A few single dark pixels inside Copper and Platinum (one third of a point on the phone).
- Bronze ring is brighter and more golden than before (the dark dashed groove was the defect).
