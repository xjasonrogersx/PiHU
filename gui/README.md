```
sudo apt-get update
sudo apt-get install python3-tk

pip install -r requirements.txt

```

## Test1

Just an example

<img width="650" height="661" alt="image" src="https://github.com/user-attachments/assets/8ae2c5cd-0135-433b-9841-80e9116de89a" />

## Test2

- Uses MQTT ( speed published with pub.py car/speed )
- background image can be change with keys 1,2,3. message published to car/HU/bg_image

- uses a bit of hack to fix the corner issue - it fills with the top left colour of the backround image

<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/72e096da-7ca3-48e4-80d2-cba50ed21973" />


## Test3

- Compositing with PIL. this handles transparncy and test outline.

<img width="1088" height="870" alt="image" src="https://github.com/user-attachments/assets/a6033fab-8919-4dcc-b862-89b0e1c3b70a" />

## font

https://www.1001fonts.com/nunito-font.html

```
mkdir /usr/share/fonts/truetype/custom
cp nunito.black.ttf /usr/share/fonts/truetype/custom/.
fc-cache -f -v


root@529aca652eda:/workspace/PiHU/gui/test# python3 ./testfont.py
('Standard Symbols PS', 'Century Schoolbook L', 'DejaVu Math TeX Gyre', 'URW Gothic', 'CustomTkinter_shapes_font', 'Nunito', 'Nimbus Roman', 'DejaVu Sans Mono', 'Roboto', 'URW Palladio L', 'Nimbus Sans', 'URW Gothic L', 'Dingbats', 'URW Chancery L', 'FreeSerif', 'Nimbus Mono PS', 'DejaVu Sans', 'Nimbus Sans Narrow', 'URW Bookman', 'DejaVu Sans', 'DejaVu Serif', 'Noto Sans Mono', 'DejaVu Sans', 'C059', 'Liberation Sans Narrow', 'Liberation Mono', 'Nimbus Sans L', 'Droid Sans Fallback', 'Z003', 'Standard Symbols L', 'D050000L', 'Nimbus Mono L', 'Roboto', 'Liberation Serif', 'Nimbus Roman No9 L', 'Liberation Sans', 'FreeSans', 'Noto Mono', 'P052', 'DejaVu Serif', 'FreeMono', 'URW Bookman L')



```
