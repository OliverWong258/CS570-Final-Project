#!/bin/bash

# 1. delete old .class files
rm -f *.class

# 2. compile Java files
javac SequenceAligner.java

# 3. excute SequenceAligner
# $1 means input file path
# $2 means output file path
java -XX:-UseTLAB SequenceAligner "$1" "$2"