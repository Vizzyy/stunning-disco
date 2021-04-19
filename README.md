```
BARNEY-MBP:stunning-disco barney$ ./scripts/deploy.py -h
usage: deploy.py [-h] [--lambdas] [--web] [--sam] [--api] [--all] [--delete] [--debug]

Parameterized deployment script for Stunning-Disco.

optional arguments:
-h, --help     show this help message and exit
--lambdas, -l  Deploy lambda code.
--web, -w      Deploy front-end web-resources.
--sam, -s      Package and deploy SAM template.
--api, -g      Deploy API Gateway stage.
--all, -a      Deploy all resources.
--delete, -d   Delete existing stack resources.
--debug, -o    Enable debugging output.
```