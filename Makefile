build:
	sort songs/index.tex > songs/index.sorted.tex
	mv songs/index.sorted.tex songs/index.tex
	rm sb.mx* || true
	pdflatex sb.tex </dev/null
	musixflx sb
	python3 genindex.py
	pdflatex sb.tex </dev/null

watch:
	while true; do make build; inotifywait -re modify . ; done
