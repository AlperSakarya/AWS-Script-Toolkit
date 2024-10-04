# Handy-EC2
Handy little python tool for daily AWS EC2 usage.<br>
Replace your commonly used ssh key at below line<br>
```
# ######################################## #
# REPLACE THIS WITH YOUR PRIVATE KEY
# ######################################## #
ssh_keyPath = "/your/keydir/mykey.pem"
# ######################################## #
```

## Sample output

```
##########################################################################################
TOTAL INSTANCES: 4
1 Instance: i-48904890 || State: running || Public IP: 54.119.119.119 
Name: My App Server
2 Instance: i-4a484890 || State: stopped || Public IP: 54.119.119.119 
Name: Windows 2012
3 Instance: i-c0648900 || State: running || Public IP: 54.119.119.119 
Name: Amazon LINUX
4 Instance: i-10048900 || State: stopped || Public IP: 52.119.119.119 
Name: My DB Server
##########################################################################################
REFRESH  - Press 0
START    - Press 1
STOP     - Press 2
SSH      - Press 3
EXIT     - Press 9
```