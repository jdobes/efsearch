# efsearch

    docker-compose up --build

## Release

    dnf install -y qemu-user-static # needed for buildah cross-arch build

    podman login docker.io

    podman build -f ./Dockerfile --platform linux/amd64,linux/arm64 --manifest efsearch .
    podman manifest inspect efsearch
    podman manifest push --all efsearch docker://docker.io/jdobes/efsearch:$(git rev-parse --short HEAD)
    podman manifest rm efsearch

## Debug in container

    python3 -m backend.scheduler.schedule_single_cli article 567890

