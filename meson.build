project(
  'PydSEAMSlib',
  'cpp',
  version: '2.1.0',
  default_options: ['warning_level=1', 'cpp_std=c++20'],
  meson_version: '>=1.3.0',
)

# C++ engine. Bindings live here; seams-core is the library, not a monolith.
seams = subproject(
  'seams-core',
  default_options: [
    'default_library=static',
    'with_python=false',
    'with_tests=false',
    'with_lua=disabled',
  ],
)
yds_dep = seams.get_variable('yds_dep')

nanobind_dep = dependency('nanobind')

py = import('python').find_installation(pure: false)

_link_args = []
if host_machine.system() == 'linux'
  _link_args += ['-Wl,--enable-new-dtags']
endif

py.extension_module(
  '_core',
  'src/bindings.cpp',
  dependencies: [yds_dep, nanobind_dep],
  link_args: _link_args,
  install: true,
  subdir: 'pydseamslib',
  limited_api: '3.12',
)

py.install_sources(
  [
    'src/pydseamslib/__init__.py',
    'src/pydseamslib/frame.py',
    'src/pydseamslib/aseio.py',
    'src/pydseamslib/io.py',
    'src/pydseamslib/solvis.py',
  ],
  pure: false,
  subdir: 'pydseamslib',
)

py.install_sources(
  [
    'src/pydseamslib/adapters/__init__.py',
    'src/pydseamslib/adapters/_ase.py',
  ],
  pure: false,
  subdir: 'pydseamslib/adapters',
)
