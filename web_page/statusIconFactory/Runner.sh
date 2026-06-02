#!/bin/bash

rm -f *.jpg

magick -size 40x24 xc:black status0.jpg
magick status0.jpg -fill darkgreen -draw "rectangle 2,2 37,21" status0.jpg
magick status0.jpg -font JetBrainsMono-NF-Bold -pointsize 12 -fill white -gravity Center -annotate +0+0 "Pass" status0.jpg

magick -size 40x24 xc:black status1.jpg
magick status1.jpg -fill lightgreen -draw "rectangle 2,2 37,21" status1.jpg
magick status1.jpg -font JetBrainsMono-NF-Bold -pointsize 12 -fill black -gravity Center -annotate +0+0 "Known" status1.jpg

magick -size 40x24 xc:black status2.jpg
magick status2.jpg -fill yellow -draw "rectangle 2,2 37,21" status2.jpg
magick status2.jpg -font JetBrainsMono-NF-Bold -pointsize 12 -fill black -gravity Center -annotate +0+0 "Skip" status2.jpg

magick -size 40x24 xc:black status8.jpg
magick status8.jpg -fill red -draw "rectangle 2,2 37,21" status8.jpg
magick status8.jpg -font JetBrainsMono-NF-Bold -pointsize 12 -fill black -gravity Center -annotate +0+0 "Data" status8.jpg

magick -size 40x24 xc:black status9.jpg
magick status9.jpg -fill darkred -draw "rectangle 2,2 37,21" status9.jpg
magick status9.jpg -font JetBrainsMono-NF-Bold -pointsize 12 -fill white -gravity Center -annotate +0+0 "Reply" status9.jpg

exit 0

