test:
	pytest -q

compose-up:
	docker compose up --build

compose-down:
	docker compose down -v

k8s-apply:
	kubectl apply -k k8s/overlays/dev
