# TODO

- ~add --dry-run~
- ~add --id~
- Logging
  - Logging the exact rendered YAML before build.
  - Using structured log output (JSON lines or tagged timestamps) for each image build.
- Error recovery
- If ubuntu-image fails for one host, you currently mark a global flag and continue.
  - You could go one better:
	-	Summarise which hosts failed at the end.
 	-	Offer --resume or --retry for failed ones.
- store built images in artifactory
- ansible read ubuntu-image config dry run
- TODO? split config into cluster, hardware and defaults?