:: Move up to main directory
cd ..

:: Translates from Windows-style to Unix-style paths in volume definitions
:: https://docs.docker.com/compose/reference/envvars/
SET COMPOSE_CONVERT_WINDOWS_PATHS=1

:: Run docker
docker-compose up

:: Don't just vanish after doing it
cmd /k
