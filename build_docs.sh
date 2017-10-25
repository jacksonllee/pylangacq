#!/usr/bin/env bash

BUILDPATH=docs
SOURCEPATH=docs/source

rm $BUILDPATH/*.html
sphinx-build -b html $SOURCEPATH $BUILDPATH

echo 'Documentation website in '$BUILDPATH
