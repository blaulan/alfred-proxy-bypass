#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eric Wu
# @Date:   2013-12-04 15:24:56
# @Email:  me@blaulan.com
# @Last modified by:   Eric Wu
# @Last Modified time: 2013-12-04 21:22:39

import os
import sys
import alfred
import subprocess


class bypass:
    def __init__(self):
        self.bypassList = []
        self.cmdList = {
            "search": self.bypassSearch,
            "add": self.bypassAdd,
            "rm": self.bypassRemove,
        }
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
            return "Add '%s' to bypass list." % rule
        else:
            return "Rule '%s' already exist." % rule

    def bypassRemove(self, rule):
        if rule in self.bypassList:
            self.bypassList.remove(rule)
            return "Remove '%s' from bypass list." % rule
        else:
            return "Rule '%s' not exist." & rule

    def bypassSet(self):
        cmd = ["networksetup", "-setproxybypassdomains", "Wi-Fi"]
        for item in self.bypassList:
            cmd.append(item)
        subprocess.call(cmd)
        self.bypassUpdate()

    def bypassUpdate(self):
        self.bypassList = []
        cmd = ["networksetup", "-getproxybypassdomains", "Wi-Fi"]
        output = subprocess.check_output(cmd)
        for item in output.split("\n"):
            self.bypassList.append(item)
        with open("bypass", "w") as bypassFile:
            bypassFile.write(output)

    def bypassSearch(self, rule):
        inList = []
        for item in self.bypassList:
            if rule in item:
                inList.append(item)
        self.showResult(rule, inList)
        return "Now You See Me."

    def showResult(self, rule, inList):
        n = 1
        items = []
        if rule not in self.bypassList:
            items.append(self.parse(0, "add", rule, "select to add rule"))
        for item in inList:
            items.append(self.parse(n, "rm", item, "select to remove rule"))
        alfred.write(alfred.xml(items))

    def parse(self, uid, action, title, subtitle):
        return alfred.Item(
            attributes={
                'uid': alfred.uid(uid),
                'arg': "%s %s" % (action, title)},
            title=title,
            subtitle=subtitle,
            )

    def run(self, cmd, rule):
        back = self.cmdList[cmd](rule)
        if cmd != "search":
            self.bypassSet()
            sys.stdout.write(back)


if __name__ == '__main__':
    bypass().run(sys.argv[1], sys.argv[2])
