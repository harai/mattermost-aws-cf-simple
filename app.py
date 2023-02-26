#!/usr/bin/env python3
import subprocess

import aws_cdk as cdk

from mattermost.ami.template import AmiTemplate
from mattermost.main.template import MainTemplate
from mattermost.nvirginia.template import NvirginiaTemplate

app = cdk.App(
    outdir='work',
    default_stack_synthesizer=cdk.DefaultStackSynthesizer(
        generate_bootstrap_version_rule=False))
AmiTemplate(app)
NvirginiaTemplate(app)
MainTemplate(app)
app.synth()

subprocess.run(
    'echo $(tput setaf 2)Templates are generated.$(tput sgr0)', shell=True)
