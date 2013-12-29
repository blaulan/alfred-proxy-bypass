#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eric Wu
# @Date:   2013-12-04 15:24:56
# @Email:  me@blaulan.com
# @Last modified by:   Eric Wu
# @Last Modified time: 2013-12-27 17:18:14

import sys
import alfred
import subprocess


def confirm(msg):
    applescript = """
set output to button returned of (display dialog ¬
"%s" with title ¬
"Are you fucking sure to add domains below to bypass?" buttons {"Yes", "No"} ¬
default button 2 ¬
with icon caution)
do shell script "echo " & quoted form of output"""
    cmd = "osascript -e '{}'".format(applescript % msg)
    return subprocess.check_output(cmd, shell=True).strip() == "Yes"


def parse(uid, action, title, subtitle):
    return alfred.Item(
        attributes={
            'uid': alfred.uid(uid),
            'arg': action,
            },
        title=title.replace("+", ", "),
        subtitle=subtitle,
        icon="icon.png",
        )


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
        subprocess.check_output(cmd+self.bypassList)

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
        if confirm(output):
            for item in output.split():
                if item == "*.":
                    continue
                self.bypassAdd(item)
            return "Add all items in '%s' to list." % domain

    def bypassShow(self, inList, items=None):
        if items is None:
            items = []
        for index, item in enumerate(inList):
            items.append(parse(index+1, "rm %s" % item, item, "REMOVE RULE"))
        alfred.write(alfred.xml(items))

    def bypassSearch(self, rule):
        items = self.verifyDomain(rule)
        inList = [item for item in self.bypassList if rule in item]
        self.bypassShow(inList, items)

    def verifyDomain(self, domain):
        if self.bypassHellOn:
            title = domain
            subtitle = "ADD ALL ITEMS"
            action = "add %s -a" % title
        else:
            title = ""
            subtitle = "ADD RULE"
            for item in domain.split("+"):
                if item not in self.bypassList:
                    title += "+%s" % item
                    if len(item.split(".")) == 2:
                        title += "+*.%s" % item
            title = title[1:]
            action = "add %s" % title
        return ([parse(0, action, title, subtitle)] if title else [])


if __name__ == '__main__':
    bp = bypass()
    if len(sys.argv) == 2:
        bp.bypassShow(reversed(bp.bypassList[-9:]))
        sys.exit()
    config = sys.argv[1:]
    if "-a" in config:
        bp.bypassHellOn = True
        config.remove("-a")
    callback = bp.cmdList[config[0]](config[1])
    if callback:
        bp.bypassSet()
        sys.stdout.write(callback)
