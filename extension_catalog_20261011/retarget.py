#!/usr/bin/env python3
"""Point the two app extensions at the icon-only ExtensionAssets.xcassets.

Usage: python3 retarget.py <input project.pbxproj> <output project.pbxproj>

Reads the input text, applies six edits, and writes only the output file.
Exits nonzero without writing anything if an anchor line is missing or appears
more than once, or if one of the new object IDs is already in use.

Edits (see .claude/plans/2026-10-11-extension-icon-catalog.md, Step 2):
  1. add the ExtensionAssets.xcassets file reference after the Assets.xcassets one
  2. add it to the same group, after the Assets.xcassets child
  3. replace the two old extension build-file definitions (E04, E05) with the new ones (E07, E08)
  4. swap the two extension Resources-phase lines from E04/E05 to E07/E08
"""
import sys

NEW_FILE_REFERENCE_ID = "A55E7CA7A100000000A55E06"
NEW_MONITOR_BUILD_FILE_ID = "A55E7CA7A100000000A55E07"
NEW_SHIELD_ACTION_BUILD_FILE_ID = "A55E7CA7A100000000A55E08"
OLD_MONITOR_BUILD_FILE_ID = "A55E7CA7A100000000A55E04"
OLD_SHIELD_ACTION_BUILD_FILE_ID = "A55E7CA7A100000000A55E05"

APP_CATALOG_FILE_REFERENCE_LINE = (
    "\t\tA55E7CA7A100000000A55E01 /* Assets.xcassets */ = {isa = PBXFileReference; "
    "lastKnownFileType = folder.assetcatalog; name = Assets.xcassets; "
    "path = ScreenTime/SupportingFiles/Assets.xcassets; sourceTree = SOURCE_ROOT; };"
)
EXTENSION_CATALOG_FILE_REFERENCE_LINE = (
    f"\t\t{NEW_FILE_REFERENCE_ID} /* ExtensionAssets.xcassets */ = {{isa = PBXFileReference; "
    "lastKnownFileType = folder.assetcatalog; name = ExtensionAssets.xcassets; "
    "path = ScreenTime/SupportingFiles/ExtensionAssets.xcassets; sourceTree = SOURCE_ROOT; };"
)

APP_CATALOG_GROUP_CHILD_LINE = "\t\t\t\tA55E7CA7A100000000A55E01 /* Assets.xcassets */,"
EXTENSION_CATALOG_GROUP_CHILD_LINE = f"\t\t\t\t{NEW_FILE_REFERENCE_ID} /* ExtensionAssets.xcassets */,"


def old_build_file_line(build_file_id):
    return (
        f"\t\t{build_file_id} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; "
        "fileRef = A55E7CA7A100000000A55E01 /* Assets.xcassets */; };"
    )


def new_build_file_line(build_file_id):
    return (
        f"\t\t{build_file_id} /* ExtensionAssets.xcassets in Resources */ = {{isa = PBXBuildFile; "
        f"fileRef = {NEW_FILE_REFERENCE_ID} /* ExtensionAssets.xcassets */; }};"
    )


def old_phase_line(build_file_id):
    return f"\t\t\t\t{build_file_id} /* Assets.xcassets in Resources */,"


def new_phase_line(build_file_id):
    return f"\t\t\t\t{build_file_id} /* ExtensionAssets.xcassets in Resources */,"


def fail(message):
    print(f"retarget.py: {message}", file=sys.stderr)
    sys.exit(1)


def strip_line_ending(line):
    return line.rstrip("\r\n")


def line_ending_of(line):
    return line[len(strip_line_ending(line)):]


def indexes_of_line(lines, wanted_text):
    return [i for i, line in enumerate(lines) if strip_line_ending(line) == wanted_text]


def single_index_of_line(lines, wanted_text):
    found = indexes_of_line(lines, wanted_text)
    if len(found) != 1:
        fail(f"expected exactly one line {wanted_text!r}, found {len(found)}")
    return found[0]


def retarget(project_text):
    for new_id in (NEW_FILE_REFERENCE_ID, NEW_MONITOR_BUILD_FILE_ID, NEW_SHIELD_ACTION_BUILD_FILE_ID):
        if new_id in project_text:
            fail(f"new ID {new_id} is already used in the input")

    lines = project_text.splitlines(keepends=True)

    # Find every anchor against the untouched list first, so a missing one fails before any edit.
    file_reference_index = single_index_of_line(lines, APP_CATALOG_FILE_REFERENCE_LINE)
    group_child_index = single_index_of_line(lines, APP_CATALOG_GROUP_CHILD_LINE)
    monitor_definition_index = single_index_of_line(lines, old_build_file_line(OLD_MONITOR_BUILD_FILE_ID))
    shield_action_definition_index = single_index_of_line(lines, old_build_file_line(OLD_SHIELD_ACTION_BUILD_FILE_ID))
    monitor_phase_index = single_index_of_line(lines, old_phase_line(OLD_MONITOR_BUILD_FILE_ID))
    shield_action_phase_index = single_index_of_line(lines, old_phase_line(OLD_SHIELD_ACTION_BUILD_FILE_ID))

    ending = line_ending_of(lines[file_reference_index])

    # In-place replacements keep every index valid; the two insertions come last, later line first.
    lines[monitor_definition_index] = new_build_file_line(NEW_MONITOR_BUILD_FILE_ID) + ending
    lines[shield_action_definition_index] = new_build_file_line(NEW_SHIELD_ACTION_BUILD_FILE_ID) + ending
    lines[monitor_phase_index] = new_phase_line(NEW_MONITOR_BUILD_FILE_ID) + ending
    lines[shield_action_phase_index] = new_phase_line(NEW_SHIELD_ACTION_BUILD_FILE_ID) + ending

    insertions = [
        (file_reference_index, EXTENSION_CATALOG_FILE_REFERENCE_LINE + ending),
        (group_child_index, EXTENSION_CATALOG_GROUP_CHILD_LINE + ending),
    ]
    for anchor_index, new_line in sorted(insertions, reverse=True):
        lines.insert(anchor_index + 1, new_line)

    return "".join(lines)


def main():
    if len(sys.argv) != 3:
        fail("usage: python3 retarget.py <input> <output>")
    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8", newline="") as input_file:
        project_text = input_file.read()

    edited_text = retarget(project_text)

    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        output_file.write(edited_text)


if __name__ == "__main__":
    main()
