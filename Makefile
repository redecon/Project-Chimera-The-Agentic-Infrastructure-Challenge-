IMAGE_NAME = project-chimera
setup:
    # Build Docker image
	docker build -t $(IMAGE_NAME) .
test:
    # Run tests inside Docker
	docker run --rm -v "/mnt/c/Users/mella/Project_Chimera:/app" project-chimera python -m pytest tests/
spec-check:
	@echo "Running spec compliance check..."
	@if grep -q "trend_id" specs/technical.md; then \
		echo "✓ Spec check passed: trend_id found"; \
	else \
		echo "✗ Spec check failed: trend_id missing"; exit 1; \
	fi
	@if grep -q "name" specs/technical.md; then \
		echo "✓ Spec check passed: name found"; \
	else \
		echo "✗ Spec check failed: name missing"; exit 1; \
	fi
	@if grep -q "popularity_score" specs/technical.md; then \
		echo "✓ Spec check passed: popularity_score found"; \
	else \
		echo "✗ Spec check failed: popularity_score missing"; exit 1; \
	fi
	@if grep -q "timestamp" specs/technical.md; then \
		echo "✓ Spec check passed: timestamp found"; \
	else \
		echo "✗ Spec check failed: timestamp missing"; exit 1; \
	fi
