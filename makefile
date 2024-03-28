# CONNECTION_STRING=postgres://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE}?sslmode=disable
CONNECTION_STRING=postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable
# migrate-check:
# 	@if ! command -v migrate &> /dev/null; then \
#         go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest; \
#     fi

migrate-up:
	@migrate -path db/migrations -database "$(CONNECTION_STRING)" up

migrate-down:
	@migrate -path db/migrations -database "$(CONNECTION_STRING)" down

migrate-create:
	@if [ -z "$(NAME)" ]; then \
		read -p "Enter the name of the migration: " name; \
	else \
		name=$(NAME); \
	fi; \
	migrate create -ext sql -dir db/migrations -seq $$name

migrate-version:
	@migrate -path db/migrations -database "$(CONNECTION_STRING)" version

migrate-force:
	@migrate -path db/migrations -database "$(CONNECTION_STRING)" force $(VERSION)

.PHONY: migrate-up migrate-down migrate-create migrate-version migrate-force