The saved ruby_heart.blend contains the complete delivered badge and its reference. The reference, gold grain and studio world are packed in the Blender file. The OSL file and four numeric linear studio maps beside it reproduce the existing native ruby optical model for development. They contain studio light, not gem appearance pictures.

geometry.npz holds the exact delivered frame and gem arrays. Run package.py with the Blender bundled Python to package those arrays using the preserved approved gold and material graph from ruby_heart_smooth_20261112/mobile/ruby_heart.usdz. The script also copies its output into this badge folder mobile/ruby_heart.usdz.

build_cut_live.py is the editable cut builder for the live Blender connection. It writes a separate rebuild folder, preserving the delivered geometry. A changed rebuild still needs Blender renders and final native preview review before delivery.
