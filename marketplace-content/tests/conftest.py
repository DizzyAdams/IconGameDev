import sys
import os
import importlib.util

# Add the marketplace-content root and src directories to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'src'))

scripts_dir = os.path.join(base_dir, 'scripts')

# Dynamically load the hyphenated scripts and register them in sys.modules
spec_skin = importlib.util.spec_from_file_location("skin_pack_gen", os.path.join(scripts_dir, "generate-all-skin-packs.py"))
skin_pack_gen = importlib.util.module_from_spec(spec_skin)
sys.modules["skin_pack_gen"] = skin_pack_gen
spec_skin.loader.exec_module(skin_pack_gen)

spec_tex = importlib.util.spec_from_file_location("texture_pack_gen", os.path.join(scripts_dir, "generate-texture-packs.py"))
texture_pack_gen = importlib.util.module_from_spec(spec_tex)
sys.modules["texture_pack_gen"] = texture_pack_gen
spec_tex.loader.exec_module(texture_pack_gen)

spec_build = importlib.util.spec_from_file_location("build_all", os.path.join(scripts_dir, "build-all.py"))
build_all = importlib.util.module_from_spec(spec_build)
sys.modules["build_all"] = build_all
spec_build.loader.exec_module(build_all)
