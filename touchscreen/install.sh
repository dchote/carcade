#!/bin/sh
cp tap_to_click.py /usr/local/bin && chmod 755 /usr/local/bin/tap_to_click.py
cp tap-to-click.service /etc/systemd/system && chmod 644 /etc/systemd/system/tap-to-click.service
systemctl daemon-reload
-systemctl enable tap-to-click
systemctl start tap-to-click