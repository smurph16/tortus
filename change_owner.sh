#! /bin/bash
chown -R www-data:www-data /usr/local/share/moin/eduwiki
service apache2 restart
