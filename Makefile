build:
	rm sb.mx* || true
	pdflatex sb.tex </dev/null
	musixflx sb
	pdflatex sb.tex </dev/null

watch:
	while true; do make build; inotifywait -e modify . ; done
