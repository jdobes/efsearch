# efsearch

    docker-compose up --build

## Debug in container

    podman exec -it efs-scheduler bash
    python3 -m backend.scheduler.schedule_single_cli article 567890

## Check the DB

    podman exec -it efs-db psql -U efs_db_user efsearch
