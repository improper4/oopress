#!/bin/bash

##--
# 上传到又拍云
##--

HOST="v0.ftp.upyun.com"

USER="username"  #指定用户名
PASS="password"  #指定密码
LCD="./_site"  #指定本地目录
RCD="remotepath" #指定远程目录


lftp -c "open ftp://$HOST;
user $USER $PASS;
lcd $LCD;
cd $RCD;
mirror –reverse \
–delete \
–dereference \
–verbose "
