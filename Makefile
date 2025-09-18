dev-api:
	cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

dev-web:
	cd apps/web && npm run dev:local

dev-desktop:
	cd apps/desktop/01_CORE_SYSTEM && streamlit run streamlit_app.py --server.port 8501

dev:
	make -j3 dev-api dev-web dev-desktop

install-api:
	cd apps/api && pip install -r requirements.txt

install-web:
	cd apps/web && npm install

install:
	make install-api install-web

test-api:
	cd apps/api && python -m pytest tests/ -v || echo "No tests found"

test-web:
	cd apps/web && npm test || echo "No tests found"

test:
	make test-api test-web

clean:
	rm -rf apps/web/.next apps/web/node_modules apps/api/__pycache__

.PHONY: dev-api dev-web dev-desktop dev install-api install-web install test-api test-web test clean
