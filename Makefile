build:
	pdflatex sb.tex </dev/null

watch:
	while true; do make build; inotifywait -e modify . ; done
