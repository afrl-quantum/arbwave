# vim: ts=2:sw=2:tw=80:nowrap

### BEGIN TEMPORARY CONFIG ###
config =  {
  "MOT Loading": [
    ["MOT Detuning", 'v + 1', '1.3'],
  ],
  "Compressed MOT":[
    ["MOT Detuning", '100', '100m'],
  ],
  "Magnetic Capture":[
    ["MOT Power", '100', '10m'],
    ["U Current", '100', '10m'],
    ["Z Current", '100', '10m'],
  ],
  "Magnetic Release":[
    ["Z Current", '10 * v/x', '10']
  ],
} 
devs = dict.fromkeys([
  '/dev0/ao0',
  '/dev0/ao1',
  '/dev0/ao2',
  '/dev0/ao3',
  '/viewpoint/io0',
  '/viewpoint/io1',
  '/viewpoint/io2',
  '/viewpoint/io3',
])
### END TEMPORARY CONFIG ###



