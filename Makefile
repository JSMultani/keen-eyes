.PHONY: test run-demo plan clean

test:
	python -m unittest discover -s tests

plan:
	python -m keen_eyes.cli.main plan --task tasks/sample-feature.md

run-demo:
	python -m keen_eyes.cli.main run --task tasks/sample-feature.md --project examples/secure_document_workflow --out runs/sample

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in [pathlib.Path('runs'), pathlib.Path('build'), pathlib.Path('dist')]]"

