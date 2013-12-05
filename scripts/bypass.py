#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eric Wu
# @Date:   2013-12-04 15:24:56
# @Email:  me@blaulan.com
# @Last modified by:   Eric Wu
# @Last Modified time: 2013-12-05 12:21:38

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
        self.bypassList = []
        self.cmdList = {
            "search": self.bypassSearch,
            "add": self.bypassAddAll,
            "rm": self.bypassRemove,
        }
        self.bypassHellOn = False
        self.bypassRead()

    def bypassRead(self):
        try:
            with open("bypass", "r") as bypassFile:
                for item in bypassFile.readlines():
                    self.bypassList.append(item.strip())
        except IOError:
            self.bypassUpdate()

    def bypassAdd(self, rule):
        if rule not in self.bypassList:
            self.bypassList.append(rule)

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
                self.bypassAdd(item)
            return "Add all items in '%s' to list." % domain
        else:
            return ""

    def bypassRemove(self, rule):
        if rule in self.bypassList:
            self.bypassList.remove(rule)
            return "Remove '%s' from list." % rule
        else:
            return ""

    def bypassSet(self):
        cmd = ["networksetup", "-setproxybypassdomains", self.deviceName]
        for item in self.bypassList:
            cmd.append(item)
        output = subprocess.check_output(cmd)
        self.bypassUpdate()

    def bypassUpdate(self):
        self.bypassList = []
        cmd = ["networksetup", "-getproxybypassdomains", self.deviceName]
        output = subprocess.check_output(cmd)
        for item in output.split():
            self.bypassList.append(item)
        with open("bypass", "w") as bypassFile:
            bypassFile.write(output)

    def bypassSearch(self, rule):
        inList = [item for item in self.bypassList if rule in item]
        self.showResult(rule, inList)
        return "Now You See Me."

    def showResult(self, rule, inList):
        items = self.verifyDomain(rule)
        for item in inList:
            items.append(self.parse("rm %s" % item, item, "REMOVE RULE"))
        alfred.write(alfred.xml(items))

    def verifyDomain(self, rule):
        subtitle = ""
        action = "add %s" % " ".join(sys.argv[2:])
        #if "." not in rule:
        #    action = ""
        #    rule = "NOT A VALID DOMAIN."
        #    subtitle = "PLEASE EDIT YOUR INPUT"
        if self.bypassHellOn:
            subtitle = "ADD ALL ITEMS"
        elif rule not in self.bypassList:
            subtitle = "ADD RULE"
        return ([self.parse(action, rule, subtitle)] if subtitle else [])

    def parse(self, action, title, subtitle):
        return alfred.Item(
            attributes={
                'uid': alfred.uid(title),
                'arg': action,
                },
            title=title.replace("+", ", "),
            subtitle=subtitle,
            icon="icon.png",
            )

    def run(self, cmd, rule):
        if len(sys.argv) >= 4 and sys.argv[3] == "-a":
            self.bypassHellOn = True
        back = self.cmdList[cmd](rule)
        if cmd != "search" and back:
            self.bypassSet()
            sys.stdout.write(back)


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        bypass().run(sys.argv[1], sys.argv[2])
