{
  lib,
  python3,
  meson,
  ninja,
  pkg-config,
  eigen,
  blas,
  lapack,
  libhwy,
  llvmPackages,
  stdenv,
  fetchFromGitHub,
  seams-core-src,
}:

let
  nanobindSrc = fetchFromGitHub {
    owner = "wjakob";
    repo = "nanobind";
    rev = "v2.14.0";
    hash = "sha256-aa829i7/R5TN++/VVZDGrPFLBrfZcdXC/cfvovRX8/8=";
  };
  robinMapSrc = fetchFromGitHub {
    owner = "Tessil";
    repo = "robin-map";
    rev = "v1.4.0";
    hash = "sha256-Hkgxiq2i0TuqMK/bI5OMOn3LkmSE40NimDjK1FBZpsA=";
  };
in
python3.pkgs.buildPythonPackage {
  pname = "pydseamslib";
  version = "2.2.0";
  pyproject = true;

  src = lib.fileset.toSource {
    root = ./..;
    fileset = lib.fileset.unions [
      ../meson.build
      ../pyproject.toml
      ../README.md
      ../src
      ../tests
      ../subprojects/nanobind.wrap
      ../subprojects/robin-map.wrap
      ../subprojects/packagefiles
    ];
  };

  nativeBuildInputs = [
    meson
    ninja
    pkg-config
    python3.pkgs.meson-python
  ];

  build-system = [ python3.pkgs.meson-python ];

  buildInputs = [
    eigen
    blas
    lapack
    libhwy
    python3.pkgs.nanobind
  ]
  ++ lib.optionals stdenv.cc.isClang [ llvmPackages.openmp ];

  dependencies = [ python3.pkgs.numpy ];

  nativeCheckInputs = [
    python3.pkgs.pytest
    python3.pkgs.hypothesis
  ];

  # meson-python drives configure. The meson setup hook would leave
  # pypa looking at the build directory as if it were the project.
  dontUseMesonConfigure = true;
  dontUseMesonInstall = true;
  mesonAutoFeatures = "disabled";

  postPatch = ''
    mkdir -p subprojects
    cp -r ${seams-core-src} subprojects/seams-core
    chmod -R u+w subprojects/seams-core
    rm -rf subprojects/seams-core/subprojects

    cp -r ${nanobindSrc} subprojects/nanobind-2.14.0
    chmod -R u+w subprojects/nanobind-2.14.0
    cp subprojects/packagefiles/nanobind/meson.build subprojects/nanobind-2.14.0/meson.build
    sed -i "/version: run_command/,/).stdout().strip(),/c\\  version: '2.14.0'," \
      subprojects/nanobind-2.14.0/meson.build

    cp -r ${robinMapSrc} subprojects/robin-map-1.4.0
    chmod -R u+w subprojects/robin-map-1.4.0
    cat > subprojects/robin-map-1.4.0/meson.build <<'EOF'
    project('robin-map', 'cpp', version: '1.4.0')
    robin_map_dep = declare_dependency(
      include_directories: include_directories('include'))
    meson.override_dependency('robin-map', robin_map_dep)
    meson.override_dependency('tsl-robin-map', robin_map_dep)
    EOF
  '';

  # meson-python already installs the extension; skip wrapping
  # seams-core as a second prefix.
  mesonInstallFlags = [ "--skip-subprojects" ];

  pytestFlags = [ "tests/python" ];

  pythonImportsCheck = [
    "pydseams"
    "pydseams.yoda"
    "pydseamslib"
  ];

  meta = {
    description = "Python bindings for the d-SEAMS C++ engine";
    homepage = "https://github.com/d-SEAMS/PydSEAMSlib";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux ++ lib.platforms.darwin;
  };
}
