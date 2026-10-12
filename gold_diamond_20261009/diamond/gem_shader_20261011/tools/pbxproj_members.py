"""pbxproj_members.py <metal|kernel|unmetal> : hand-edits ScreenTime.xcodeproj/project.pbxproj (never xcodegen).
metal   : BadgeGemSurface.metal in the ScreenTime and ScreenTime-UIOnly Sources phases (Step 2).
kernel  : GemFacetPlanes.swift in the ScreenTime, ScreenTime-UIOnly and ScreenTimeTests Sources phases (Step 6).
unmetal : exact inverse of metal (used only if the Step 2 probe has to be reverted)."""
import sys

PBX = '/Users/antonioperedo/Desktop/screen_time/ScreenTime.xcodeproj/project.pbxproj'
text = open(PBX).read()

GROUP_ANCHOR = '\t\t\t\tBADE00030000000000000F0B /* BadgeNavigation.swift */,\n'
FILEREF_ANCHOR = '\t\tBADE00030000000000000F0B /* BadgeNavigation.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = BadgeNavigation.swift; sourceTree = "<group>"; };\n'
BUILDFILE_ANCHOR = '\t\tBADE00030000000000000B17 /* BadgeNavigation.swift in Sources */ = {isa = PBXBuildFile; fileRef = BADE00030000000000000F0B /* BadgeNavigation.swift */; };\n'
# Each Sources phase is found through the BadgeMorphGeometry.swift line it already holds.
PHASE_ANCHORS = {
    'screentime': '\t\t\t\tBADE00030000000000000B13 /* BadgeMorphGeometry.swift in Sources */,\n',
    'uionly': '\t\t\t\tBADE00030000000000000B14 /* BadgeMorphGeometry.swift in Sources */,\n',
    'tests': '\t\t\t\tBADE00030000000000000B15 /* BadgeMorphGeometry.swift in Sources */,\n',
}


def insert_after(source, anchor, addition):
    assert source.count(anchor) == 1, f'anchor not unique or missing: {anchor!r}'
    return source.replace(anchor, anchor + addition)


def remove_exact(source, line):
    assert source.count(line) == 1, f'line not unique or missing: {line!r}'
    return source.replace(line, '')


def add_file(source, name, kind, ref_id, build_ids):
    """build_ids maps 'screentime' / 'uionly' / 'tests' to the PBXBuildFile id for that phase."""
    assert ref_id not in source, f'{ref_id} already used'
    file_ref = f'\t\t{ref_id} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = {kind}; path = {name}; sourceTree = "<group>"; }};\n'
    source = insert_after(source, FILEREF_ANCHOR, file_ref)
    source = insert_after(source, GROUP_ANCHOR, f'\t\t\t\t{ref_id} /* {name} */,\n')
    for phase, build_id in build_ids.items():
        assert build_id not in source, f'{build_id} already used'
        build_file = f'\t\t{build_id} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {ref_id} /* {name} */; }};\n'
        source = insert_after(source, BUILDFILE_ANCHOR, build_file)
        source = insert_after(source, PHASE_ANCHORS[phase], f'\t\t\t\t{build_id} /* {name} in Sources */,\n')
    return source


def remove_file(source, name, ref_id, build_ids):
    source = remove_exact(source, f'\t\t{ref_id} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.metal; path = {name}; sourceTree = "<group>"; }};\n')
    source = remove_exact(source, f'\t\t\t\t{ref_id} /* {name} */,\n')
    for build_id in build_ids.values():
        source = remove_exact(source, f'\t\t{build_id} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {ref_id} /* {name} */; }};\n')
        source = remove_exact(source, f'\t\t\t\t{build_id} /* {name} in Sources */,\n')
    return source


METAL_IDS = {'screentime': 'BADE00030000000000000B20', 'uionly': 'BADE00030000000000000B21'}
KERNEL_IDS = {'screentime': 'BADE00030000000000000B22', 'uionly': 'BADE00030000000000000B23', 'tests': 'BADE00030000000000000B24'}

mode = sys.argv[1]
if mode == 'metal':
    text = add_file(text, 'BadgeGemSurface.metal', 'sourcecode.metal', 'BADE00030000000000000F20', METAL_IDS)
elif mode == 'kernel':
    text = add_file(text, 'GemFacetPlanes.swift', 'sourcecode.swift', 'BADE00030000000000000F21', KERNEL_IDS)
elif mode == 'unmetal':
    text = remove_file(text, 'BadgeGemSurface.metal', 'BADE00030000000000000F20', METAL_IDS)
else:
    sys.exit('mode must be metal, kernel or unmetal')
open(PBX, 'w').write(text)
print('ok', mode)
