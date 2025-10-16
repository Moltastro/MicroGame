from preset import *
step_size=4
for x in range(step_size+1):
    for y in range(step_size+1):
        xcor=x*240/step_size-120
        ycor=150-y*300/step_size
        GameObject(xcor,ycor,Rectangle(5,5,color=rgb(0, 195, 255)))
        offset=20
        if x%2:
            offset*=-1
        GameObject(xcor,ycor+offset,Text(f"{int(xcor)},{int(ycor)}",color=rgb(255, 0, 0)))

game.update()