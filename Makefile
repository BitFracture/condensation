
# Set up commands to run
RUN := chmod u+x ./scripts/run.sh ; ./scripts/run.sh
DEPLOY := chmod u+x ./scripts/deploy.sh ; ./scripts/deploy.sh
ifeq ($(OS),Windows_NT)
	RUN := scripts\run.bat
	DEPLOY := scripts\deploy.bat
endif

# Do what the user requested
deploy:
	$(DEPLOY)
run:
	$(RUN)
