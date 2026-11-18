.PHONY: help up down logs psql benchmark-mvt ingest-tn19 check-rust test-python tiles-tn19

help:
	@echo "SolarGIS Digital Twin - Command Reference"
	@echo "  make up            - Start PostGIS 16-3.4, Redis 7, Rust Backend, AI Worker"
	@echo "  make down          - Stop all containers"
	@echo "  make psql          - Open interactive psql shell inside PostGIS container"
	@echo "  make benchmark-mvt - Seed 36,544 synthetic TN19 modules & run EXPLAIN ANALYZE (ST_AsMVT vs GeoJSON)"
	@echo "  make ingest-tn19   - Ingest data/gpkg/thuannam19_master.gpkg into PostGIS"
	@echo "  make check-rust    - Run cargo check on Module 3 Rust workspace"
	@echo "  make test-python   - Run pytest on spatial_grid_index and modules"
	@echo "  make tiles-tn19    - Build XYZ WebP & PMTiles for Thuan Nam 19"

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f

psql:
	docker exec -it solargis_postgis psql -U solargis -d solargis_db

benchmark-mvt:
	docker exec -it solargis_postgis psql -U solargis -d solargis_db -c "SELECT seed_synthetic_tn19_modules(36544); ANALYZE solar_modules; EXPLAIN (ANALYZE, BUFFERS) SELECT OCTET_LENGTH(get_solar_modules_mvt(18, 209348, 122145, 1));"

ingest-tn19:
	python infra/postgres/ingest_gpkg_to_postgis.py --gpkg data/gpkg/thuannam19_master.gpkg --plant TN19

check-rust:
	cd modules/module3_digital_twin_app && cargo check --workspace

test-python:
	pytest packages/spatial_grid_index/tests

tiles-tn19:
	bash modules/module1_ortho_pipeline/scripts/04_build_pmtiles.sh
