#!/bin/bash

domains=`curl -sL $1| grep -Eo 'https?://\S+/'| awk -F/ '{print $3}'|grep -vF '"'|grep -vF '>'|grep -vF ')'| grep -Eo '([^\.\s]+\.co\.[^\.\s]+$)|([^\.\s]+\.[^\.\s]+$)'| sort -u|grep -vF .cn`

add_list=`echo $domains|xargs`
add_list2=$(echo "$add_list"|sed 's/^/\*./g;s/ / *./g')
echo $add_list
echo $add_list2
