helm upgrade --install \
	--namespace riab \
	--values ./helm-charts/mobi-expert-xapp/values.yaml \
	mobi-expert-xapp \
	./helm-charts/mobi-expert-xapp/ && \
	sleep 20 && \
	kubectl wait pod -n riab --for=condition=Ready -l app=mobi-expert-xapp --timeout=600s
