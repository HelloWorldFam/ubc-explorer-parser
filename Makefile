SITEDIR := v-env/lib/python3.8/site-packages
LAMBDA := lambdaPackage

.PHONY: clean all

all: v-env/bin/activate ${LAMBDA}.zip

v-env/bin/activate: requirements.txt
	test -d v-env || python3.8 -m venv v-env
	. v-env/bin/activate && pip install --upgrade pip && pip install -r $< && deactivate
	touch $@

v-env/lib/python3.8/site-packages/%.zip: ${SITEDIR}
	cd $<; zip -r9 $(notdir $@) .

%.zip: ${SITEDIR}/%.zip $(wildcard *.py)
	cp -v $< .
	zip -r9 $@ $(filter %.py,$^)

clean:
	@echo "cleaning directory for git commits ..."
	rm -rf v-env
