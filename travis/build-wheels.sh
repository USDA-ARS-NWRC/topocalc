#!/bin/bash
# Adapated from https://github.com/pydata/pandas-manylinux/blob/master/travis/build-wheels.sh
set -e -x

echo ${PYVER}

PYBIN=/opt/python/${PYVER}/bin

# Compile wheels
echo "building for ${PYBIN}"
${PYBIN}/pip install -r /io/requirements.txt
${PYBIN}/pip install nose
${PYBIN}/pip wheel --no-deps /io/ -w wheelhouse/

# Bundle external shared libraries into the wheels
for whl in wheelhouse/topocalc*.whl; do
    auditwheel repair $whl -w /io/wheelhouse/
done

# Install packages and test
${PYBIN}/pip install topocalc --no-index -f /io/wheelhouse
${PYBIN}/pip show topocalc
cd ${HOME}
${PYBIN}/nosetests -vv --exe topocalc