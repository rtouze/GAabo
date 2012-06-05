
                      Logiciel de gestion d'abonnés GA abo
                   ------------------------------------------

Sorry for English speakers but this piece of software is designed for French
Magazines.

Il s'agit d'un logiciel de gestion d'abonnés réalisé pour les besoins du
magazine [Grandir Autrement](http://www.grandirautrement.com).

Ce logiciel est écrit en Python, il a été testé sur GNU Debian 6, Windows XP et 7.
Il nécessite l'installation des logiciels suivants pour fonctionner :

* [Python 2.7](http://www.python.org/download/)
* [wxPython](http://www.wxpython.org/download.php#stable) (attention : prendre la version unicode) 

Pour le lancer, exécuter le script gaabo.py du répertoire src.

Il se base sur une base de donnée sqlite3 pour créer et modifier des abonnés.

Il permet une recherche d'abonnés à partir de leur nom, entreprise et adresse email.

Il permet d'exporter un listing d'abonnés pour l'envoi des numéros et des
hors-série pour le site [www.routage-en-ligne.com](http://www.routage-en-ligne.com) et ainsi générér des
étiquettes de routage.

Il permet d'exporter des listing d'abonnés pour faire des campagnes de
réabonnement par mail et courrier.
