#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eric Wu
# @Date:   2013-12-04 15:24:56
# @Email:  me@blaulan.com
# @Last modified by:   Eric Wu
# @Last Modified time: 2013-12-06 10:56:33

import os
import sys
import alfred
import subprocess

applescript = """
set output to button returned of (display dialog ¬
"%s" with title ¬
"Are you fucking sure to add domains below to bypass?" buttons {"Yes", "No"} ¬
default button 2 ¬
with icon caution)
do shell script "echo " & quoted form of output"""

class bypass:
    def __init__(self):
        self.deviceName = "Wi-Fi"
        self.cmdList = {
            "search": self.bypassSearch,
            "add": self.bypassAddAll,
            "rm": self.bypassRemove,
        }
        self.bypassHellOn = False
        self.bypassRead()

    def bypassRead(self):
        self.bypassList = []
        cmd = ["networksetup", "-getproxybypassdomains", self.deviceName]
        output = subprocess.check_output(cmd)
        for item in output.split():
            self.bypassList.append(item)

    def bypassSet(self):
        cmd = ["networksetup", "-setproxybypassdomains", self.deviceName]
        output = subprocess.check_output(cmd+self.bypassList)

    def bypassAdd(self, rule):
        if rule not in self.bypassList:
            self.bypassList.append(rule)

    def bypassRemove(self, rule):
        if rule in self.bypassList:
            self.bypassList.remove(rule)
            return "Remove '%s' from list." % rule

    def bypassAddAll(self, rule):
        if self.bypassHellOn:
            return self.bypassHell(rule)
        else:
            for item in rule.split("+"):
                self.bypassAdd(item)
            return "Add '%s' to list." % rule.replace("+", "', '")

    def bypassHell(self, domain):
        cmd = ["sh", "bypass.sh", domain]
        output = subprocess.check_output(cmd)
        confirm = "osascript -e '{}'".format(applescript % output)
        if subprocess.check_output(confirm, shell=True).strip() == "Yes":
            for item in output.split():
                if item == "*.": continue
                self.bypassAdd(item)
            return "Add all items in '%s' to list." % domain

    def bypassSearch(self, rule):
        items = self.verifyDomain(rule)
        inList = [item for item in self.bypassList if rule in item]
        for index, item in enumerate(inList):
            items.append(self.parse(index+1, "rm %s" % item, item, "REMOVE RULE"))
        alfred.write(alfred.xml(items))

    def verifyDomain(self, domain):
        subtitle = ""
        action = "add %s" % domain
        if self.bypassHellOn:
            subtitle = "ADD ALL ITEMS"
            action = "add %s -a" % domain
        elif domain not in self.bypassList:
            subtitle = "ADD RULE"
            if len(domain.split(".")) == 2:
                domain = "{0}, *.{0}".format(domain)
                action = "add %s" % domain.replace(", ", "+")
        return ([self.parse(0, action, domain, subtitle)] if subtitle else [])

    def parse(self, uid, action, title, subtitle):
        return alfred.Item(
            attributes={
                'uid': alfred.uid(uid),
                'arg': action,
                },
            title=title.replace("+", ", "),
            subtitle=subtitle,
            icon="icon.png",
            )

    def run(self):
        config = sys.argv[1:]
        if "-a" in config:
            self.bypassHellOn = True
            config.remove("-a")
        cmd, rule = config[0], config[1]
        callback = self.cmdList[cmd](rule)
        if callback:
            self.bypassSet()
            sys.stdout.write(callback)

if __name__ == '__main__':
    bypass().run()
