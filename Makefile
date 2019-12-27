up: web dns

web:
	bash -c "python3 run.py"

dns:
	bash - c "cd dns && python3 server"

.PHONY: web dns