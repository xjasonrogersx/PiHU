
```
sudo apt-get update
sudo apt-get install python3-tk

pip install -r requirements.txt

```




## font

https://www.1001fonts.com/nunito-font.html


```
root@529aca652eda:/workspace/PiHU/gui/test# mkdir /usr/share/fonts/truetype/custom
root@529aca652eda:/workspace/PiHU/gui/test# cp nunito.black.ttf /usr/share/fonts/truetype/custom/.
root@529aca652eda:/workspace/PiHU/gui/test# fc-cache -f -v


root@529aca652eda:/workspace/PiHU/gui/test# python3 ./testfont.py 
('Standard Symbols PS', 'Century Schoolbook L', 'DejaVu Math TeX Gyre', 'URW Gothic', 'CustomTkinter_shapes_font', 'Nunito', 'Nimbus Roman', 'DejaVu Sans Mono', 'Roboto', 'URW Palladio L', 'Nimbus Sans', 'URW Gothic L', 'Dingbats', 'URW Chancery L', 'FreeSerif', 'Nimbus Mono PS', 'DejaVu Sans', 'Nimbus Sans Narrow', 'URW Bookman', 'DejaVu Sans', 'DejaVu Serif', 'Noto Sans Mono', 'DejaVu Sans', 'C059', 'Liberation Sans Narrow', 'Liberation Mono', 'Nimbus Sans L', 'Droid Sans Fallback', 'Z003', 'Standard Symbols L', 'D050000L', 'Nimbus Mono L', 'Roboto', 'Liberation Serif', 'Nimbus Roman No9 L', 'Liberation Sans', 'FreeSans', 'Noto Mono', 'P052', 'DejaVu Serif', 'FreeMono', 'URW Bookman L')



```

