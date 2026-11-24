.PHONY: lint test check smoke stop status

lint:
	python3 tools/check_layers.py

test:
	python3 -m unittest discover -s tests -v

check: lint test

smoke:
	python3 tools/smoke_test.py

stop:
	@if [ -f logs/server.pid ]; then kill $$(cat logs/server.pid) 2>/dev/null || true; rm -f logs/server.pid; echo "伺服器已停止"; else echo "沒有執行中的伺服器紀錄"; fi

status:
	python3 tools/feature_status.py --check-baseline
