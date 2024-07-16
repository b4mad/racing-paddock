FROM quay.io/fedora/python-312@sha256:584a5c31c483ce13ce0f112cd9c7dcdf6cc3c808a62d5c0c55e0281df62bd3f6

LABEL \
    name="b4mad-racing-paddock" \
    io.k8s.display-name="B4mad Racing Paddock" \
    vendor="#B4mad" \
    maintainer="B4mad" \
    org.opencontainers.image.source="https://github.com/b4mad/racing" \
    org.opencontainers.image.description="This is the #B4mad Racing Paddock component" \
    org.opencontainers.image.licenses="GPL-3.0-or-later" \
    license="GPL-3.0-or-later" \
    org.opencontainers.image.base.name="quay.io/fedora/python-310" \
    org.opencontainers.image.url="https://github.com/b4mad/racing/" \
    io.openshift.non-scalable=true

ENV \
    DISABLE_SETUP_PY_PROCESSING=1 \
    DISABLE_PYPROJECT_TOML_PROCESSING=1 \
    ENABLE_MICROPIPENV=1

USER 0
ADD . /tmp/src
RUN /usr/bin/fix-permissions /tmp/src
USER 1001

RUN /usr/libexec/s2i/assemble

CMD /usr/libexec/s2i/run
