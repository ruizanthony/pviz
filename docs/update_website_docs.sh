#!/bin/bash
make html
rsync ./build/html/ ruizanthony:~/public_html/pviz/docs
