#!/bin/sh

# Script de creation de packet pour gaabo. Utilise ce qu'il y a dans le repertoire src
# Parametre : nom de version, format

VERSION=$1
TYPE=$2
packet_name=gaabo_${VERSION}

echo "Creation de ${packet_name}"

mkdir ${packet_name}
cp src/*.py ${packet_name}

case ${TYPE} in
    zip) zip -r ${packet_name}.zip ${packet_name};;
    gz) tar czf ${packet_name}.tar.gz ${packet_name};;
    bz2) tar cjf ${packet_name}.tar.bz2 ${packet_name};;
    *) echo "Mauvais type"; exit 1;;
esac

zipped=`ls ${packet_name}.*`
echo "Le packet ${zipped} est genere"
exit 0
