#!/bin/bash

openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
cat cert.pem key.pem > out.pem
rm cert.pem key.pem
