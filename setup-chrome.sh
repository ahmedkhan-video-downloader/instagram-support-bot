#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y wget unzip curl gnupg
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
