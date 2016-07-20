#!bin/bash
zip package.zip weeklytime.py
zip -r package.zip config.py
cd ./env/lib/python2.7/site-packages/
zip -r ../../../../package.zip *
