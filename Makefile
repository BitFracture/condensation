
# Set up commands to run
RUN := chmod u+x ./run.sh ; ./run.sh
DEPLOY := chmod u+x ./deploy.sh ; ./deploy.sh
ifeq ($(OS),Windows_NT)
	RUN := run.bat
	DEPLOY := deploy.bat
endif

# Do what the user requested
deploy:
	$(DEPLOY)
run:
	$(RUN)
