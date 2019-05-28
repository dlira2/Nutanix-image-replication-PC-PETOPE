# Nutanix-image-replication-PC-PETOPE
Script designed to replicate images between prism element connected to the same prism central in a simple way.
 
Within the prism element of nutanix when uploading an image (ISO or VMDK), it is only available for this cluster. If this prism element is connected to a Prism central with multiple clusters it is possible to replicate the prism element image to other prism element using Prism Central (Yes, it is confusing). First it is necessary to update the Prism Central catalog so that the metadata of the image can be found in Prism Element already available within Prism Central, then the image can be replicated to another Prism Element.

Another case, if the image of the prism element is in an "ACTIVE" state while in another group it is "INACTIVE" it is possible to use this script to leave "ACTIVE".

the copy command unfortunately can only be done through SSH, the script is designed to provide 100% feedback from the APIs provided by Nutanix. Only the execution of the command is through SSH.
The monitoring of the copy job is monitored by API.

Requirements:

     -Python 3.6 or higher.
     -Admin user for PE and PC.
     -The password of the PC and PE user must be the same. (It is modifiable, however, themes of simplicity is preferable in this way).
     -Password for SSH to PC ( Prism Central).

Python Module :

     -import getpass 
     -import paramiko 
     -import json 
     -import requests 
     -import urllib3 
     -import datetime 
     -import datetime
     -import re
