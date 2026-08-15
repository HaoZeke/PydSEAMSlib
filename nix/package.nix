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
  seams-core-src,
}:

python3.pkgs.buildPythonPackage {
  pname = "pydseams";
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

  mesonAutoFeatures = "disabled";

  postPatch = ''
    mkdir -p subprojects
    cp -r ${seams-core-src} subprojects/seams-core
    chmod -R u+w subprojects/seams-core
  '';

  # meson-python already installs the extension; skip wrapping
  # seams-core as a second prefix.
  mesonInstallFlags = [ "--skip-subprojects" ];

  pytestFlags = [ "tests/python" ];

  pythonImportsCheck = [
    "pydseams"
    "pydseamslib"
  ];

  meta = {
    description = "Python bindings for the d-SEAMS C++ engine";
    homepage = "https://github.com/d-SEAMS/PydSEAMSlib";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux ++ lib.platforms.darwin;
  };
}
