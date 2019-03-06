



# Welcome to  SMART- TAP-BOT



  > **NOTE:**  This Page gives overall API descriptions

# commands
 ## **tap :** 
> **IP:PORT/tap?Point="XY coordinate"**
> example: 192.168.0.115:5000/tap?Point=""X100 Y150"
#### response:
 ```json

    "tap to point X100 Y150 recieved"

```

 ## **swipe :** 
> **IP:PORT/swipe?startPoint="XY coordinate"&endpoint="XY coordinate"**
> example: 192.168.0.115:5000/swipe?startPoint=""X100 Y150"&endPoint="X60 Y80"
> 
#### response:
 ```json

    "swipe from X100 Y150 to X60 Y80 done"

```
 ## **one point move :** 
*moves to a point specified*

> **IP:PORT/opMove?Point="XY coordinate"**
> example: 192.168.0.115:5000/opMove?Point=""X100 Y150"
#### response:
 ```json

    "move to single point X100 Y150 recieved"

```
 ## **two point move :** 
*moves between two points*
> **IP:PORT/tpMove?Point1="XY coordinate"&Point2="XY coordinate"**
> example: 192.168.0.115:5010/tpMove?Point1=""X100 Y150"&Point2="X100 Y20"
#### response:
 ```json

    "move between two point "X100 Y150" "X100 Y20"  recieved"

```
 ## **home :** 
 *command to manually home the axis*
> **IP:PORT/home**
> example: 192.168.0.115:5010/home
#### response:
 ```json

  "homing done"

```

 ## **setAngle :** 
 *calibrate the linear servo angle*
> **IP:PORT/setAngle?initial=value1&final=value2**
> example: 192.168.0.115:5010/setAngle?initial=80&final=50
#### response:
 ```json
  "setting angle initial =80 final =50 done"

```

 ## **testTap :** 
 *tap at the current position*
> **IP:PORT/testTap**
> example: 192.168.0.115:5010/testTap
#### response:
 ```json
   "test tap done initial=100 final=150"
```

 ## **change speed :** 
 *change the speed of X Y axis movement*
> **IP:PORT/setSpeed?speed=value**
> example: 192.168.0.115:5010/setSpeed?speed=500
#### response:
 ```json
   "speed set 500"

```

 ## **Get current Position :** 
 *gets the current position of tap head*
> **IP:PORT/currentpos**
> example: 192.168.0.110:5000/currentpos
#### response:
 ```json
    "current position X:100 Y:100"

```
 ## **Set Home Position :** 
 *set the current position as (0,0) use negative coordinate if necessary*
> **IP:PORT/setpositionhome**
> example: 192.168.0.110:5000/setpositionhome
#### response:
 ```json
    "set position 0,0 done"

```
 ## **Disable/Enable motors :** 
 *disable/enable motors if required*
> **IP:PORT/motorSatus**
> example: 192.168.0.110:5000/motorstatus
#### response:
 ```json

    "motor disable= True"

```

